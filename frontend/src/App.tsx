import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ContractDetail from "./pages/ContractDetail";
import Contracts from "./pages/Contracts";
import Dashboard from "./pages/Dashboard";
import InvestigationDetail from "./pages/InvestigationDetail";
import Investigations from "./pages/Investigations";
import Upload from "./pages/Upload";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="contracts" element={<Contracts />} />
          <Route path="contracts/:contractId" element={<ContractDetail />} />
          <Route path="investigations" element={<Investigations />} />
          <Route path="investigations/:investigationId" element={<InvestigationDetail />} />
          <Route path="upload" element={<Upload />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
