import React from 'react'
import { FormField, FormItem, FormLabel, FormDescription, FormControl, FormMessage } from '../ui/form';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { FormInputProps } from './form-types';

type FormTextInputProps = FormInputProps & {
  description?: string;
  multiline?: boolean;
  type?: string;
  outline?: boolean;
  onKeyDown?: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
};

export function FormTextInput(props: FormTextInputProps) {
  const {
    form,
    name,
    label,
    inputProps,
    placeholder,
    description,
    multiline,
    type = "text",
    inputClassName,
    containerClassName,
    showError = true,
    outline = true,
    onEnter: onEnterPressed,
  } = props;

  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => {
        return (
            <div className={containerClassName}>
                <FormItem>
                    {label ? <FormLabel>{label}</FormLabel> : null}
                    {description ? <FormDescription>{description}</FormDescription> : null}
                    <FormControl className={inputClassName}>
                    {/* Using onInput because onChange doesn't trigger when autofilling information */}
                    {multiline ? (
                        <Textarea
                        placeholder={placeholder}
                        onInput={form.onChange}
                        draggable={false}
                        outline={outline}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && onEnterPressed != null) {
                            e.preventDefault();
                            onEnterPressed(e)
                          }
                        }}
                        {...field}
                        {...inputProps}
                        />
                    ) : (
                        <Input
                        className='w-full'
                        placeholder={placeholder}
                        type={type}
                        outline={outline}
                        onInput={form.onChange}
                        {...field}
                        {...inputProps}
                        />
                    )}
                    </FormControl>
                    {showError && <FormMessage />}
                </FormItem>
            </div>
        );
      }}
    />
  );
}