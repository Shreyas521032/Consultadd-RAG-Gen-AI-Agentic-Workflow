// Simplified version of the toast component
import { toast as sonnerToast } from "@/components/ui/toast"

export const toast = ({ title, description, variant, duration = 5000 }) => {
  sonnerToast({
    title,
    description,
    variant,
    duration,
  })
}

