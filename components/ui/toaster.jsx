import React from "react";
import { Toaster as HotToaster } from "react-hot-toast";

export function Toaster() {
  return <HotToaster position="top-right" reverseOrder={false} />;
}