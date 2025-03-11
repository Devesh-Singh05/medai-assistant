export type UserRole = "doctor" | "radiologist"

export interface LoginCredentials {
  email: string
  password: string
  role: UserRole
}