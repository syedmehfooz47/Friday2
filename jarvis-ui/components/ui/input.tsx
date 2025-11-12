import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const inputVariants = cva(
  "flex items-center w-full rounded-md border border-input bg-background text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      size: {
        default: "h-10 px-3 py-2",
        sm: "h-9 px-3",
        lg: "h-11 px-8",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface InputRootProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof inputVariants> {}

const InputRoot = React.forwardRef<HTMLDivElement, InputRootProps>(
  ({ className, size, ...props }, ref) => {
    return (
      <div
        className={cn("relative", className)}
        ref={ref}
        {...props}
      />
    )
  }
)
InputRoot.displayName = "InputRoot"


const InputIcon = React.forwardRef<
  React.ElementRef<"div">,
  React.HTMLAttributes<HTMLDivElement> & {
    asChild?: boolean
  }
>(({ className, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "div"
    return (
        <Comp
        ref={ref}
        className={cn(
            "absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground",
            className
        )}
        {...props}
        />
    )
})
InputIcon.displayName = 'InputIcon'


export interface InputFieldProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const InputField = React.forwardRef<HTMLInputElement, InputFieldProps>(
  ({ className, type, ...props }, ref) => {
    const hasIcon = React.useContext(InputIconContext)
    return (
      <input
        type={type}
        className={cn(
          inputVariants({ size: hasIcon ? "lg" : "default" }), // Use lg size padding for icon
          "w-full",
          {"pl-10": hasIcon}, // Add padding if icon is present
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
InputField.displayName = "InputField"


// Context to detect if an Icon is being used
const InputIconContext = React.createContext(false)

const Input = ({className, ...props}: InputFieldProps) => {
    const hasIcon = React.Children.toArray(props.children).some(
        (child) => React.isValidElement(child) && child.type === InputIcon
    )
    return (
        <InputIconContext.Provider value={hasIcon}>
            <InputRoot className={className}>
                {props.children}
            </InputRoot>
        </InputIconContext.Provider>
    )
}

export { Input, InputRoot, InputField, InputIcon }

