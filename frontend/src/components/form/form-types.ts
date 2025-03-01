import type { ReactNode } from "react";

export type FormInputProps = {
  form: any;
  inputProps?: Record<string, any>;
  isDisabled?: boolean;
  label: ReactNode;
  name: string;
  placeholder?: string;
  inputClassName?: string;
  containerClassName?: string;
  showError?: boolean;
  onEnter?: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
};