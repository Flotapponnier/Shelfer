export enum ValidationState {
  PENDING = "pending",
  APPROVED = "approved",
  DECLINED = "declined",
}

export interface FieldValidation {
  [fieldPath: string]: ValidationState
}

export interface ValidationAction {
  type: "APPROVE" | "DECLINE"
  fieldPath: string
  originalValue?: any
}
