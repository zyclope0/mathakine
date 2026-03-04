"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { DiagnosticSolver } from "@/components/diagnostic/DiagnosticSolver";

function DiagnosticPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const from = searchParams.get("from");
  const triggeredFrom = from === "onboarding" ? "onboarding" : "settings";

  const handleComplete = () => {
    router.replace("/dashboard");
  };

  return (
    <main className="min-h-screen px-4 py-8">
      <DiagnosticSolver triggeredFrom={triggeredFrom} onComplete={handleComplete} />
    </main>
  );
}

export default function DiagnosticPage() {
  return (
    <ProtectedRoute>
      <DiagnosticPageContent />
    </ProtectedRoute>
  );
}
