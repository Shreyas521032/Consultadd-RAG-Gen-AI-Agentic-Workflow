import { Button } from "@/components/ui/button";
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h2 className="mb-4 font-semibold text-primary">404 Not Found</h2>
      <p className="text-lg text-gray-500 mb-8">The page you are looking for does not exist.</p>
      <Link href="/">
        <Button variant="outline">Return Home</Button>
      </Link>
    </div>
  );
}
