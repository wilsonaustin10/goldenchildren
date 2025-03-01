'use client';

import { zodResolver } from '@hookform/resolvers/zod';

import { useForm } from "react-hook-form";
import { z } from "zod";
import { Form } from './ui/form';

import { Button } from './ui/button';
import { FormTextInput } from './form/FormTextInput';
import { Send, SendHorizonal } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Message } from '@/types/Message';

type P = {
  onSubmit: (values: z.infer<typeof formSchema>) => void;
  messages: Message[];
  isGenerating: boolean;
}

export const formSchema = z.object({
    text: z.string().min(1, { message: "Required" }),
})

export default function ChatWidgetForm({onSubmit, isGenerating, messages}: P) {

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      text: "",
    },
  });

  const handleSubmit = async (values: z.infer<typeof formSchema>) => {
    if (formSchema.safeParse(values).success) {
      form.reset();
      return onSubmit(values);
    }
  }

  const handleEnterPressed = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
    if (!isGenerating) {
      form.handleSubmit(handleSubmit)();
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)}>
        <div className='bg-neutral-700 rounded'>
          <FormTextInput
            containerClassName='grow' 
            inputClassName="bg-neutral-700"
            form={form} 
            multiline
            label={null}
            showError={false}
            outline={false}
            name="text" 
            onEnter={handleEnterPressed}
            onKeyDown={handleEnterPressed}
            placeholder="Type a message..." />
          
          <div className='flex justify-between justify-end px-2 pb-2'>
            <Button disabled={isGenerating} type="submit" className={cn(
              `ml-2 rounded-full w-8 h-8 p-2`,
            )}>
              <SendHorizonal size={16} color={"white"} />
            </Button>
          </div>
        </div>
      </form>
    </Form>
  )
}