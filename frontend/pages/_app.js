import "@/styles/globals.css";
import Layout from "../components/Layout";
import { OneDriveProvider } from "../context/OneDriveContext";

export default function App({ Component, pageProps }) {
  return (
    <OneDriveProvider>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </OneDriveProvider>
  );
}