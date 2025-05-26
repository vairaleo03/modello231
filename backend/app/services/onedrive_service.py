import os
import msal
import time
import requests
import json
import logging
from io import BytesIO
from dotenv import load_dotenv
from fastapi import HTTPException, Request
from typing import Tuple, Dict, Optional, Union, Any

load_dotenv()

# ⭐ SETUP LOGGING GLOBALE
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Recupera credenziali da variabili d'ambiente
CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "consumers")  # Default a "consumers" per account personali
REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI")

# Verifica che le variabili siano impostate
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    logger.warning("⚠️ Attenzione: Variabili d'ambiente per Microsoft Graph API non configurate correttamente")
    print("⚠️ Attenzione: Variabili d'ambiente per Microsoft Graph API non configurate correttamente")

# ⭐ SCOPES CORRETTI - SOLO MICROSOFT GRAPH (NO OPENID CONNECT)
SCOPES = ["https://graph.microsoft.com/Files.ReadWrite"]

class OneDriveService:
    """
    Servizio per l'integrazione con Microsoft OneDrive tramite Microsoft Graph API.
    Supporta sia account personali (consumers) che business (tenant specifico).
    Gestisce autenticazione, token e operazioni sui file.
    """
    
    def __init__(self):
        """Inizializza il servizio OneDrive con le credenziali Microsoft."""
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.tenant_id = TENANT_ID
        self.authority = f"https://login.microsoftonline.com/{TENANT_ID}"
        self.scopes = SCOPES
        self.redirect_uri = REDIRECT_URI
        
        # Determina il tipo di account
        self.is_personal_account = TENANT_ID.lower() in ["consumers", "common"]
        
        # ⭐ SETUP LOGGING CON EMOJI E DETTAGLI
        account_type = "Personal" if self.is_personal_account else "Business"
        logger.debug(f"🔧 OneDrive Service inizializzato ({account_type})")
        logger.debug(f"🔧 CLIENT_ID: {self.client_id[:8]}...")
        logger.debug(f"🔧 REDIRECT_URI: {self.redirect_uri}")
        logger.debug(f"🔧 AUTHORITY: {self.authority}")
        logger.debug(f"🔧 TENANT_ID: {self.tenant_id}")
        logger.debug(f"🔧 SCOPES: {self.scopes}")
        
        # Inizializza MSAL app
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )
        
        logger.debug(f"🔧 MSAL app inizializzata con authority: {self.authority}")
        
        # Cache dei token (in produzione usare Redis o altro storage persistente)
        self.token_cache = {}
        logger.debug(f"🔧 Token cache inizializzata")
    
    def get_auth_url(self) -> str:
        """
        Genera l'URL per l'autenticazione dell'utente.
        
        Returns:
            str: URL di autenticazione Microsoft
        """
        try:
            # ⭐ USA SOLO SCOPES MICROSOFT GRAPH (NESSUN OPENID SCOPE)
            auth_url = self.app.get_authorization_request_url(
                scopes=self.scopes,  # Solo Microsoft Graph scopes
                redirect_uri=self.redirect_uri,
                state="12345"  # In produzione: usare un valore casuale per sicurezza
            )
            
            # ⭐ LOGGING DELL'URL GENERATO CON EMOJI
            account_type = "personal" if self.is_personal_account else "business"
            logger.debug(f"🔗 Generated {account_type} auth URL: {auth_url}")
            
            return auth_url
            
        except Exception as e:
            logger.error(f"❌ Errore generazione auth URL: {str(e)}")
            raise e
    
    def get_token_from_code(self, auth_code: str) -> Tuple[str, str]:
        """
        Ottiene un token di accesso dal codice di autorizzazione.
        
        Args:
            auth_code: Codice di autorizzazione ottenuto dal flusso OAuth
            
        Returns:
            Tuple[str, str]: Coppia (access_token, user_id)
            
        Raises:
            Exception: Se non è possibile ottenere il token
        """
        # ⭐ LOGGING DEL CODICE DI SCAMBIO CON EMOJI
        account_type = "personal" if self.is_personal_account else "business"
        logger.debug(f"🔄 Exchanging code for {account_type} token: {auth_code[:10]}...")
        
        try:
            result = self.app.acquire_token_by_authorization_code(
                code=auth_code,
                scopes=self.scopes,  # Solo Microsoft Graph scopes
                redirect_uri=self.redirect_uri
            )
            
            # ⭐ LOGGING DEL RISULTATO
            logger.debug(f"📊 Token result keys: {list(result.keys())}")
            
            if "access_token" in result:
                # ⭐ LOGGING DEL SUCCESSO CON EMOJI
                logger.debug(f"✅ {account_type.title()} token acquired successfully")
                
                # ⭐ GENERAZIONE USER_ID APPROPRIATA PER TIPO ACCOUNT
                if self.is_personal_account:
                    # Per account personali, usa 'sub' o fallback
                    user_id = result.get("id_token_claims", {}).get("sub")
                    if not user_id:
                        # Fallback: usa parte del token come ID
                        user_id = f"personal_{result['access_token'][-10:]}"
                else:
                    # Per account business, usa 'oid'
                    user_id = result.get("id_token_claims", {}).get("oid", "default_user")
                
                # ⭐ LOGGING DELL'USER ID
                logger.debug(f"👤 {account_type.title()} User ID: {user_id}")
                
                expires_at = time.time() + result["expires_in"]
                token_info = {
                    "access_token": result["access_token"],
                    "refresh_token": result.get("refresh_token"),
                    "expires_at": expires_at
                }
                
                self.token_cache[user_id] = token_info
                logger.debug(f"💾 Token cached for {account_type} user {user_id}, expires at: {expires_at}")
                
                return result["access_token"], user_id
            else:
                # ⭐ LOGGING DELL'ERRORE CON EMOJI
                logger.error(f"❌ {account_type.title()} token error: {result}")
                error_msg = result.get("error_description", "Unknown error")
                raise Exception(f"Errore nell'ottenere il token {account_type}: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ Errore scambio token {account_type}: {str(e)}")
            raise e
    
    def get_valid_token(self, user_id: str) -> Optional[str]:
        """
        Verifica se il token è valido o se necessita refresh.
        
        Args:
            user_id: ID dell'utente Microsoft
            
        Returns:
            Optional[str]: Token valido o None se non disponibile
        """
        account_type = "personal" if self.is_personal_account else "business"
        logger.debug(f"🔍 Getting valid {account_type} token for user: {user_id}")
        
        if user_id not in self.token_cache:
            logger.debug(f"❌ No {account_type} token found in cache for user: {user_id}")
            return None
            
        token_info = self.token_cache[user_id]
        time_until_expiry = token_info["expires_at"] - time.time()
        
        logger.debug(f"⏰ {account_type.title()} token expires in {time_until_expiry:.0f} seconds")
        
        # Se il token sta per scadere (< 5 minuti), fai refresh
        if time_until_expiry < 300:
            logger.debug(f"🔄 {account_type.title()} token needs refresh, attempting refresh...")
            
            if token_info.get("refresh_token"):
                try:
                    result = self.app.acquire_token_by_refresh_token(
                        refresh_token=token_info["refresh_token"],
                        scopes=self.scopes
                    )
                    
                    if "access_token" in result:
                        logger.debug(f"✅ {account_type.title()} token refreshed successfully")
                        
                        # Aggiorna il token nella cache
                        self.token_cache[user_id] = {
                            "access_token": result["access_token"],
                            "refresh_token": result.get("refresh_token", token_info["refresh_token"]),
                            "expires_at": time.time() + result["expires_in"]
                        }
                        return result["access_token"]
                    else:
                        logger.error(f"❌ {account_type.title()} token refresh failed: {result}")
                        # In caso di errore, rimuovi dalla cache
                        del self.token_cache[user_id]
                        return None
                except Exception as e:
                    logger.error(f"❌ Errore refresh {account_type} token: {str(e)}")
                    del self.token_cache[user_id]
                    return None
            else:
                logger.debug(f"❌ No refresh token available for {account_type} account")
                del self.token_cache[user_id]
                return None
        
        logger.debug(f"✅ Using existing valid {account_type} token")
        return token_info["access_token"]
    
    def check_auth_status(self, user_id: str) -> bool:
        """
        Verifica se l'utente è autenticato con OneDrive.
        
        Args:
            user_id: ID dell'utente
            
        Returns:
            bool: True se autenticato, False altrimenti
        """
        is_authenticated = self.get_valid_token(user_id) is not None
        account_type = "personal" if self.is_personal_account else "business"
        logger.debug(f"🔐 {account_type.title()} auth status for user {user_id}: {is_authenticated}")
        return is_authenticated
    
    def upload_file(self, user_id: str, file_name: str, file_content: bytes, 
                   folder_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Carica un file su OneDrive dell'utente.
        
        Args:
            user_id: ID dell'utente Microsoft
            file_name: Nome del file da caricare
            file_content: Contenuto binario del file
            folder_path: Percorso della cartella su OneDrive (opzionale)
            
        Returns:
            Dict[str, Any]: Dati del file caricato
            
        Raises:
            HTTPException: Se l'autenticazione non è valida o l'upload fallisce
        """
        account_type = "personal" if self.is_personal_account else "business"
        logger.debug(f"📤 Uploading file {file_name} for {account_type} user {user_id} (size: {len(file_content)} bytes)")
        
        token = self.get_valid_token(user_id)
        if not token:
            logger.error(f"❌ No valid {account_type} token for user {user_id}")
            raise HTTPException(
                status_code=401, 
                detail=f"Token {account_type} non valido o scaduto. Necessaria riautenticazione."
            )
        
        try:
            # Gestione del percorso
            upload_path = f"/me/drive/root:/{file_name}:/content"
            if folder_path:
                # Assicurati che il percorso sia formattato correttamente
                folder_path = folder_path.strip("/")
                upload_path = f"/me/drive/root:/{folder_path}/{file_name}:/content"
                
                logger.debug(f"📁 Upload path with folder: {upload_path}")
                
                # ⭐ CREA LA CARTELLA SOLO PER ACCOUNT BUSINESS (per evitare errori su account personali)
                if not self.is_personal_account:
                    self._ensure_folder_exists(token, folder_path)
                else:
                    logger.debug("📁 Skipping folder creation for personal account")
            else:
                logger.debug(f"📁 Upload path (root): {upload_path}")
            
            # Esegui l'upload del file
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream"
            }
            
            url = f"https://graph.microsoft.com/v1.0{upload_path}"
            logger.debug(f"🌐 Making PUT request to: {url}")
            
            response = requests.put(url, headers=headers, data=file_content, timeout=60)
            
            logger.debug(f"📊 Upload response status: {response.status_code}")
            
            if response.status_code in (200, 201):
                result = response.json()
                logger.debug(f"✅ File uploaded successfully: {result.get('name')}")
                return result
            else:
                error_text = response.text or "Errore sconosciuto"
                logger.error(f"❌ Upload failed: {response.status_code} - {error_text}")
                
                # ⭐ ERRORE PIÙ SPECIFICO PER ACCOUNT PERSONALI
                if self.is_personal_account and "does not have a SPO license" in error_text:
                    raise HTTPException(
                        status_code=400,
                        detail="Account personale non supporta questa operazione. Usa un account Microsoft 365 Business o prova un provider alternativo."
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Errore nel caricamento del file: {error_text}"
                    )
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error during {account_type} upload: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Errore di rete durante upload: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error during {account_type} upload: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Errore imprevisto: {str(e)}"
            )
    
    def _ensure_folder_exists(self, token: str, folder_path: str) -> None:
        """
        Verifica che una cartella esista in OneDrive, creandola se necessario.
        ⭐ UTILIZZATO SOLO PER ACCOUNT BUSINESS
        
        Args:
            token: Token di accesso
            folder_path: Percorso della cartella da verificare/creare
            
        Raises:
            HTTPException: Se non è possibile creare la cartella
        """
        logger.debug(f"📂 Ensuring folder exists (business account): {folder_path}")
        
        folders = folder_path.split('/')
        current_path = ""
        
        for folder in folders:
            if current_path:
                current_path += f"/{folder}"
            else:
                current_path = folder
                
            logger.debug(f"🔍 Checking business folder: {current_path}")
            
            # Verifica se la cartella esiste
            headers = {"Authorization": f"Bearer {token}"}
            check_response = requests.get(
                f"https://graph.microsoft.com/v1.0/me/drive/root:/{current_path}",
                headers=headers
            )
            
            logger.debug(f"📊 Business folder check response: {check_response.status_code}")
            
            # Se non esiste (404), creala
            if check_response.status_code == 404:
                logger.debug(f"➕ Creating business folder: {folder}")
                
                create_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                parent_path = "https://graph.microsoft.com/v1.0/me/drive/root"
                if current_path != folder:  # Se non è la prima cartella, specifica il parent
                    parent_path = f"https://graph.microsoft.com/v1.0/me/drive/root:/{'/'.join(current_path.split('/')[:-1])}"
                
                create_response = requests.post(
                    f"{parent_path}/children",
                    headers=create_headers,
                    json={
                        "name": folder,
                        "folder": {},
                        "@microsoft.graph.conflictBehavior": "rename"
                    }
                )
                
                logger.debug(f"📊 Business folder creation response: {create_response.status_code}")
                
                if create_response.status_code not in (200, 201):
                    logger.error(f"❌ Failed to create business folder {folder}: {create_response.text}")
                    raise HTTPException(
                        status_code=create_response.status_code,
                        detail=f"Impossibile creare la cartella {folder}: {create_response.text}"
                    )
                else:
                    logger.debug(f"✅ Business folder created successfully: {folder}")
            else:
                logger.debug(f"✅ Business folder already exists: {current_path}")
    
    def upload_document(self, user_id: str, file_name: str, document_content: bytes, 
                       folder_path: str = "Modello231/Documenti") -> Dict[str, Any]:
        """
        Carica un documento Word su OneDrive.
        
        Args:
            user_id: ID dell'utente
            file_name: Nome del file
            document_content: Contenuto binario del documento
            folder_path: Percorso della cartella (default: Modello231/Documenti)
            
        Returns:
            Dict[str, Any]: Dati del file caricato
        """
        account_type = "personal" if self.is_personal_account else "business"
        logger.debug(f"📄 Uploading {account_type} document: {file_name} to {folder_path}")
        return self.upload_file(user_id, file_name, document_content, folder_path)
    
    def upload_transcription(self, user_id: str, transcript_id: int, document_content: bytes) -> Dict[str, Any]:
        """
        Carica una trascrizione su OneDrive.
        
        Args:
            user_id: ID dell'utente
            transcript_id: ID della trascrizione
            document_content: Contenuto binario del documento Word
            
        Returns:
            Dict[str, Any]: Dati del file caricato
        """
        file_name = f"trascrizione_{transcript_id}_{int(time.time())}.docx"
        account_type = "personal" if self.is_personal_account else "business"
        logger.debug(f"📝 Uploading {account_type} transcription {transcript_id} as {file_name}")
        return self.upload_document(user_id, file_name, document_content, "Modello231/Trascrizioni")
    
    def upload_summary(self, user_id: str, summary_id: int, document_content: bytes) -> Dict[str, Any]:
        """
        Carica un riassunto su OneDrive.
        
        Args:
            user_id: ID dell'utente
            summary_id: ID del riassunto
            document_content: Contenuto binario del documento Word
            
        Returns:
            Dict[str, Any]: Dati del file caricato
        """
        file_name = f"riassunto_{summary_id}_{int(time.time())}.docx"
        account_type = "personal" if self.is_personal_account else "business"
        logger.debug(f"📋 Uploading {account_type} summary {summary_id} as {file_name}")
        return self.upload_document(user_id, file_name, document_content, "Modello231/Riassunti")

# Istanza globale del servizio
onedrive_service = OneDriveService()