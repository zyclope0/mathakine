"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export interface FeedbackReportItem {
  id: number;
  user_id: number | null;
  username: string | null;
  feedback_type: string;
  page_url: string | null;
  exercise_id: number | null;
  challenge_id: number | null;
  description: string | null;
  status: string;
  created_at: string | null;
}

export interface AdminFeedbackResponse {
  feedback: FeedbackReportItem[];
}

export function useAdminFeedback() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin-feedback"],
    queryFn: async () => {
      return await api.get<AdminFeedbackResponse>("/api/admin/feedback");
    },
    staleTime: 30_000,
  });

  return {
    feedback: data?.feedback ?? [],
    isLoading,
    error,
    refetch,
  };
}
