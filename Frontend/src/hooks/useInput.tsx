import { useState } from "react";
import type { ChangeEvent } from "react";

type ValidationFn = (value: string) => string | null;

export default function useInput(
  initialValue: string,
  validationFn: ValidationFn | null = null,
) {
  const [value, setValue] = useState<string>(initialValue);
  const [isTouched, setIsTouched] = useState<boolean>(false);

  const error: string | null =
    validationFn && isTouched ? validationFn(value) : null;

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
    setIsTouched(false);
  };

  const handleBlur = () => {
    setIsTouched(true);
  };

  return {
    value,
    handleChange,
    handleBlur,
    error,
  };
}
