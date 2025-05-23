from fastapi import Request, Response
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Gestione sessioni senza cookie - usa solo LocalStorage + Headers
    """
    
    @staticmethod
    def set_onedrive_user_id(response: Response, request: Request, user_id: str):
        """
        ⭐ NON USA PIÙ COOKIE - solo response headers per frontend
        """
        try:
            logger.debug(f"💾 Preparando user_id per frontend: {user_id}")
            
            # ⭐ AGGIUNGI USER_ID COME HEADER PERSONALIZZATO
            response.headers["X-OneDrive-User-ID"] = user_id
            response.headers["X-Auth-Token"] = user_id
            
            logger.debug(f"✅ Headers impostati per user: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Errore impostazione headers: {str(e)}")
    
    @staticmethod
    def get_onedrive_user_id(request: Request) -> str:
        """
        ⭐ RECUPERA USER_ID DA HEADERS AUTHORIZATION
        """
        try:
            # ⭐ PRIMA STRATEGIA: Header Authorization
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                user_id = auth_header.replace("Bearer ", "").strip()
                if len(user_id) > 10:  # Validazione base
                    logger.debug(f"✅ User ID da Authorization header: {user_id}")
                    return user_id
            
            # ⭐ SECONDA STRATEGIA: Header personalizzato
            custom_header = request.headers.get("X-OneDrive-User-ID", "")
            if custom_header and len(custom_header) > 10:
                logger.debug(f"✅ User ID da header personalizzato: {custom_header}")
                return custom_header
            
            # ⭐ FALLBACK: Header alternativo
            alt_header = request.headers.get("X-Auth-Token", "")
            if alt_header and len(alt_header) > 10:
                logger.debug(f"✅ User ID da header alternativo: {alt_header}")
                return alt_header
            
            logger.debug("❌ Nessun user_id trovato negli headers")
            logger.debug(f"🔍 Authorization header: {auth_header[:20]}...")
            logger.debug(f"🔍 Headers disponibili: {list(request.headers.keys())}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore recupero headers: {str(e)}")
            return None
    
    @staticmethod
    def clear_session(response: Response):
        """Pulisce gli headers di sessione"""
        try:
            logger.debug("🗑️ Pulizia headers sessione...")
            response.headers["X-OneDrive-User-ID"] = ""
            response.headers["X-Auth-Token"] = ""
            logger.debug("✅ Headers puliti")
        except Exception as e:
            logger.error(f"❌ Errore pulizia headers: {str(e)}")
