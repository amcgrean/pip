import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '../layout/AppLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { DashboardPage } from '../pages/DashboardPage'
import { GuideEditorPage } from '../pages/GuideEditorPage'
import { GuidesPage } from '../pages/GuidesPage'
import { ImportsPage } from '../pages/ImportsPage'
import { LoginPage } from '../pages/LoginPage'
import { ProductsPage } from '../pages/ProductsPage'
import { ProductDetailPage } from '../pages/ProductDetailPage'
import { SettingsPage } from '../pages/SettingsPage'
import { VendorsPage } from '../pages/VendorsPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="products/:productId" element={<ProductDetailPage />} />
        <Route path="guides" element={<GuidesPage />} />
        <Route path="guides/:guideId" element={<GuideEditorPage />} />
        <Route path="vendors" element={<VendorsPage />} />
        <Route path="imports" element={<ImportsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
