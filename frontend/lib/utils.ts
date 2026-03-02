// Re-export depuis lib/utils/cn.ts (source de vérité unique — M15 audit).
// Les composants shadcn/UI importent depuis "@/lib/utils" ; les autres depuis "@/lib/utils/cn".
// Les deux chemins fonctionnent, la logique n'est définie qu'en un seul endroit.
export { cn } from "./utils/cn";
