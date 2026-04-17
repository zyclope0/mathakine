"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type ApiClientError } from "@/lib/api/client";

export type FeedbackStatus = "new" | "read" | "resolved";

export interface FeedbackReportItem {
  id: number;
  user_id: number | null;
  username: string | null;
  feedback_type: string;
  page_url: string | null;
  exercise_id: number | null;
  challenge_id: number | null;
  description: string | null;
  user_role: string | null;
  active_theme: string | null;
  ni_state: string | null;
  component_id: string | null;
  status: FeedbackStatus;
  created_at: string | null;
}

export interface AdminFeedbackResponse {
  feedback: FeedbackReportItem[];
}

type FeedbackReportItemApi = Omit<FeedbackReportItem, "status"> & { status: string };

interface AdminFeedbackResponseApi {
  feedback: FeedbackReportItemApi[];
}

function normalizeFeedbackStatus(raw: string): FeedbackStatus {
  const s = (raw ?? "").toLowerCase().trim();
  if (s === "new" || s === "read" || s === "resolved") {
    return s;
  }
  return "new";
}

export function useAdminFeedback() {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery<AdminFeedbackResponse, ApiClientError>({
    queryKey: ["admin-feedback"],
    queryFn: async (): Promise<AdminFeedbackResponse> => {
      const response = await api.get<AdminFeedbackResponseApi>("/api/admin/feedback");
      return {
        ...response,
        feedback: response.feedback.map((item) => ({
          ...item,
          status: normalizeFeedbackStatus(item.status),
        })),
      };
    },
    staleTime: 30_000,
  });

  const updateMutation = useMutation({
    mutationFn: async (params: { feedbackId: number; status: FeedbackStatus }) => {
      return api.patch<{ id: number; status: FeedbackStatus }>(
        `/api/admin/feedback/${params.feedbackId}`,
        { status: params.status }
      );
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-feedback"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (feedbackId: number) => {
      return api.delete<{ success: boolean; id: number }>(`/api/admin/feedback/${feedbackId}`);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-feedback"] });
    },
  });

  return {
    feedback: data?.feedback ?? [],
    isLoading,
    error,
    refetch,
    updateFeedbackStatus: updateMutation.mutateAsync,
    isUpdatingStatus: updateMutation.isPending,
    updateStatusError: updateMutation.error,
    deleteFeedback: deleteMutation.mutateAsync,
    isDeletingFeedback: deleteMutation.isPending,
    deleteFeedbackError: deleteMutation.error,
  };
}
