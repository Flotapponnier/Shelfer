import type { JsonValue } from "../types/json";
import type { ValidationAction } from "../types/validation";

export function approveAllFields(
  value: JsonValue,
  path: string[],
  onValidation: (action: ValidationAction) => void
) {
  if (value !== null && typeof value === "object") {
    if (Array.isArray(value)) {
      value.forEach((item, idx) => approveAllFields(item, [...path, `[${idx}]`], onValidation));
    } else {
      Object.entries(value).forEach(([k, v]) => approveAllFields(v, [...path, k], onValidation));
    }
  } else {
    onValidation({ type: "APPROVE", fieldPath: path.join("."), originalValue: undefined });
  }
} 