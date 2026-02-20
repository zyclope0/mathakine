"use client";

import { useState } from "react";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { Settings } from "lucide-react";
import { useAdminConfig, type AdminConfigItem } from "@/hooks/useAdminConfig";

function groupByCategory(settings: AdminConfigItem[]) {
  const groups: Record<string, AdminConfigItem[]> = {};
  for (const s of settings) {
    const cat = s.category || "autres";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(s);
  }
  const order = ["système", "features", "limites", "autres"];
  const cats = [...new Set([...order, ...Object.keys(groups)])];
  return cats.filter((c) => groups[c]?.length).map((c) => ({ category: c, items: groups[c] }));
}

function buildInitFromSettings(settings: AdminConfigItem[]) {
  const init: Record<string, boolean | number | string> = {};
  for (const s of settings) {
    init[s.key] = s.value;
  }
  return init;
}

function ConfigEditor({
  settings,
  onSave,
  isUpdating,
}: {
  settings: AdminConfigItem[];
  onSave: (local: Record<string, boolean | number | string>) => Promise<void>;
  isUpdating: boolean;
}) {
  const [local, setLocal] = useState<Record<string, boolean | number | string>>(() => buildInitFromSettings(settings));
  const [dirty, setDirty] = useState(false);

  const handleBoolChange = (key: string, checked: boolean) => {
    setLocal((p) => ({ ...p, [key]: checked }));
    setDirty(true);
  };

  const handleIntChange = (key: string, val: string) => {
    const n = parseInt(val, 10);
    if (!Number.isNaN(n)) {
      setLocal((p) => ({ ...p, [key]: n }));
      setDirty(true);
    }
  };

  const handleSave = async () => {
    try {
      await onSave(local);
      setDirty(false);
      toast.success("Paramètres enregistrés");
    } catch {
      toast.error("Erreur lors de l'enregistrement");
    }
  };

  const groups = groupByCategory(settings);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Paramètres globaux"
        description="Configuration du Temple — limites, features flags, maintenance."
        icon={Settings}
        actions={
          dirty ? (
            <Button onClick={handleSave} disabled={isUpdating}>
              {isUpdating ? "Enregistrement…" : "Enregistrer"}
            </Button>
          ) : null
        }
      />
      <PageSection>
        <div className="space-y-6">
          {groups.map(({ category, items }) => (
            <Card key={category}>
              <CardHeader className="pb-3">
                <h2 className="text-lg font-semibold capitalize">{category}</h2>
              </CardHeader>
              <CardContent className="space-y-4">
                {(items ?? []).map((item) => (
                  <div
                    key={item.key}
                    className="flex flex-wrap items-center justify-between gap-4 rounded-lg border p-4"
                  >
                    <div>
                      <Label htmlFor={item.key} className="font-medium">
                        {item.label}
                      </Label>
                      {item.min != null && item.max != null && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {item.min}–{item.max}
                        </p>
                      )}
                    </div>
                    {item.type === "bool" ? (
                      <Switch
                        id={item.key}
                        checked={Boolean(local[item.key] ?? item.value)}
                        onCheckedChange={(c) => handleBoolChange(item.key, c)}
                      />
                    ) : (
                      <Input
                        id={item.key}
                        type="number"
                        value={String(local[item.key] ?? item.value)}
                        min={item.min}
                        max={item.max}
                        className="w-28"
                        onChange={(e) => handleIntChange(item.key, e.target.value)}
                      />
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </PageSection>
    </div>
  );
}

export default function AdminConfigPage() {
  const { settings, isLoading, error, updateSettings, isUpdating } = useAdminConfig();

  const handleSave = async (local: Record<string, boolean | number | string>) => {
    await updateSettings(local);
  };

  if (isLoading) return <LoadingState />;
  if (error)
    return (
      <PageSection>
        <p className="text-destructive">Impossible de charger les paramètres.</p>
      </PageSection>
    );

  const settingsKey = settings.map((s) => `${s.key}:${s.value}`).join("|");
  return (
    <ConfigEditor
      key={settingsKey}
      settings={settings}
      onSave={handleSave}
      isUpdating={isUpdating}
    />
  );
}
