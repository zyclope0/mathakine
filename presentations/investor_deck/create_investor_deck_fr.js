const path = require("path");
const PptxGenJS = require("pptxgenjs");
const {
  autoFontSize,
  calcTextBox,
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./pptxgenjs_helpers");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Equipe Mathakine";
pptx.company = "Mathakine";
pptx.subject = "Presentation investisseurs";
pptx.title = "Mathakine - Deck investisseurs";
pptx.lang = "fr-CH";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "fr-CH",
};

const colors = {
  bg: "F7F8FC",
  navy: "0E1A3A",
  cyan: "00A3A3",
  blue: "2F80ED",
  green: "27AE60",
  red: "EB5757",
  gray700: "344054",
  gray500: "667085",
  gray300: "D0D5DD",
  white: "FFFFFF",
};

const SLIDE_W = 13.333;
const SLIDE_H = 7.5;

function addBackground(slide, title, subtitle = "") {
  slide.background = { color: colors.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: SLIDE_W,
    h: 0.58,
    fill: { color: colors.navy },
    line: { color: colors.navy },
  });

  slide.addText("Mathakine", {
    x: 0.45,
    y: 0.12,
    w: 2.3,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 14,
    bold: true,
    color: colors.white,
  });

  slide.addText(title, {
    ...autoFontSize(title, "Aptos Display", {
      x: 0.7,
      y: 0.86,
      w: 8.9,
      h: 0.78,
      minFontSize: 24,
      maxFontSize: 36,
      valign: "top",
      bold: true,
      color: colors.navy,
    }),
    fontFace: "Aptos Display",
  });

  if (subtitle) {
    slide.addText(subtitle, {
      ...calcBox(14, {
        x: 0.72,
        y: 1.62,
        w: 9.6,
        h: 0.58,
        valign: "top",
      }),
      fontFace: "Aptos",
      color: colors.gray700,
      fontSize: 14,
    });
  }

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 11.05,
    y: 0.87,
    w: 1.68,
    h: 0.42,
    rectRadius: 0.08,
    fill: { color: "E8F7F7" },
    line: { color: "BCEAEA", pt: 1 },
  });
  slide.addText("Mars 2026", {
    x: 11.22,
    y: 0.99,
    w: 1.35,
    h: 0.2,
    fontFace: "Aptos",
    fontSize: 11,
    color: colors.cyan,
    bold: true,
    align: "center",
  });
}

function finalizeSlide(slide) {
  if (process.env.SLIDE_DEBUG_WARN === "1") {
    warnIfSlideHasOverlaps(slide, pptx);
    warnIfSlideElementsOutOfBounds(slide, pptx);
  }
}

function calcBox(fontSize, opts) {
  const measured = calcTextBox(fontSize, { lines: 1, ...opts });
  return {
    ...measured,
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
  };
}

function addKpiCard(slide, x, y, w, h, label, value, delta, deltaColor) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
    shadow: { type: "outer", color: "ADB5BD", blur: 2, angle: 45, distance: 1, opacity: 0.12 },
  });
  slide.addText(label, {
    x: x + 0.22,
    y: y + 0.16,
    w: w - 0.44,
    h: 0.2,
    fontFace: "Aptos",
    fontSize: 11,
    color: colors.gray500,
  });
  slide.addText(value, {
    x: x + 0.22,
    y: y + 0.46,
    w: w - 0.44,
    h: 0.4,
    fontFace: "Aptos Display",
    fontSize: 24,
    bold: true,
    color: colors.navy,
  });
  slide.addText(delta, {
    x: x + 0.22,
    y: y + h - 0.38,
    w: w - 0.44,
    h: 0.2,
    fontFace: "Aptos",
    fontSize: 10,
    bold: true,
    color: deltaColor,
  });
}

// Slide 1: couverture
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.navy };

  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: SLIDE_W,
    h: SLIDE_H,
    fill: { color: colors.navy },
    line: { color: colors.navy },
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.95,
    y: 0.92,
    w: 5.25,
    h: 5.45,
    rectRadius: 0.2,
    fill: { color: "163062", transparency: 4 },
    line: { color: "2450A0", pt: 1 },
  });

  slide.addText("Mathakine", {
    x: 1.4,
    y: 1.42,
    w: 4.3,
    h: 0.62,
    fontFace: "Aptos Display",
    fontSize: 42,
    color: colors.white,
    bold: true,
  });

  slide.addText("L’IA qui transforme les devoirs de maths en progression mesurable", {
    ...autoFontSize("L’IA qui transforme les devoirs de maths en progression mesurable", "Aptos", {
      x: 1.4,
      y: 2.2,
      w: 4.35,
      h: 1.35,
      minFontSize: 18,
      maxFontSize: 24,
      bold: false,
      color: "E4ECFF",
      valign: "top",
    }),
    fontFace: "Aptos",
  });

  slide.addText("Seed round - 1,8 MCHF", {
    x: 1.4,
    y: 4.28,
    w: 4.1,
    h: 0.3,
    fontFace: "Aptos",
    fontSize: 16,
    color: "7EE6E6",
    bold: true,
  });

  slide.addText("Fondateurs: equipe produit, IA et pedagogie\nConfidentiel - Mars 2026", {
    x: 1.4,
    y: 5.02,
    w: 4.4,
    h: 0.72,
    fontFace: "Aptos",
    fontSize: 11,
    color: "BFD1F8",
    valign: "top",
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 6.95,
    y: 1.05,
    w: 5.5,
    h: 5.4,
    rectRadius: 0.2,
    fill: { color: "0E1A3A", transparency: 25 },
    line: { color: "00A3A3", pt: 1 },
  });

  addKpiCard(slide, 7.35, 1.48, 2.35, 1.58, "Eleves actifs / mois", "12 400", "+41% sur 6 mois", colors.green);
  addKpiCard(slide, 9.95, 1.48, 2.1, 1.58, "Ecoles partenaires", "64", "+18 ce trimestre", colors.green);
  addKpiCard(slide, 7.35, 3.3, 2.35, 1.58, "NPS enseignants", "61", "Top 10% edtech", colors.cyan);
  addKpiCard(slide, 9.95, 3.3, 2.1, 1.58, "MRR", "74 kCHF", "+9,2% MoM", colors.green);

  finalizeSlide(slide);
}

// Slide 2: probleme
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Le probleme: trop d’eleves decrochent en mathematiques",
    "Les enseignants manquent de temps pour personnaliser les exercices et suivre les blocages en continu."
  );

  const leftBox = { x: 0.7, y: 2.18, w: 6.1, h: 4.8 };
  const rightBox = { x: 7.0, y: 2.18, w: 5.62, h: 4.8 };

  slide.addShape(pptx.ShapeType.roundRect, {
    ...leftBox,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
  });

  slide.addText("Constats terrain", {
    x: 1.02,
    y: 2.42,
    w: 2.8,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 17,
    color: colors.navy,
    bold: true,
  });

  slide.addText(
    [
      { text: "1 enseignant sur 2 ", options: { bold: true, color: colors.navy } },
      { text: "declare ne pas pouvoir adapter ses devoirs au niveau reel de chaque eleve." },
      { text: "\n\n40% des eleves ", options: { bold: true, color: colors.navy } },
      { text: "en difficulte n’obtiennent pas de feedback utile avant l’evaluation suivante." },
      { text: "\n\nLes outils numeriques actuels ", options: { bold: true, color: colors.navy } },
      { text: "sont souvent generiques, peu alignes aux progressions locales et lourds a deployer." },
    ],
    {
      ...calcBox(13, {
        x: 1.02,
        y: 2.84,
        w: 5.55,
        h: 3.64,
        valign: "top",
      }),
      fontFace: "Aptos",
      color: colors.gray700,
      valign: "top",
    }
  );

  slide.addShape(pptx.ShapeType.roundRect, {
    ...rightBox,
    rectRadius: 0.08,
    fill: { color: "F2FAFA" },
    line: { color: "C6ECEC", pt: 1 },
  });

  slide.addText("Impact mesurable", {
    x: 7.32,
    y: 2.42,
    w: 2.8,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 17,
    color: colors.navy,
    bold: true,
  });

  slide.addChart(pptx.ChartType.bar, [
    { name: "Taux de reussite", labels: ["Sans support", "Avec support adapte"], values: [54, 78] },
  ], {
    x: 7.3,
    y: 2.9,
    w: 5.08,
    h: 2.28,
    barDir: "col",
    catAxisLabelFontFace: "Aptos",
    catAxisLabelSize: 10,
    valAxisMinVal: 0,
    valAxisMaxVal: 100,
    valAxisMajorUnit: 20,
    valAxisLabelSize: 10,
    chartColors: ["95A4C6", "2F80ED"],
    showValue: true,
    showLegend: false,
    dataLabelPosition: "outEnd",
    dataLabelColor: colors.navy,
    dataLabelSize: 10,
  });

  slide.addText("Ecart moyen observe apres 12 semaines sur des cohortes college.", {
    x: 7.32,
    y: 5.34,
    w: 5.0,
    h: 0.35,
    fontFace: "Aptos",
    fontSize: 10,
    color: colors.gray500,
  });

  slide.addText("La douleur est forte, frequente, et budgetee par les etablissements.", {
    ...calcBox(13, {
      x: 7.32,
      y: 5.78,
      w: 5.0,
      h: 0.9,
      bold: true,
      valign: "top",
    }),
    fontFace: "Aptos",
    color: colors.navy,
  });

  finalizeSlide(slide);
}

// Slide 3: solution
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Notre solution: un copilote pedagogique IA pour les mathematiques",
    "Mathakine adapte les parcours d’exercices, detecte les blocages et fournit des interventions actionnables aux enseignants."
  );

  const cols = [0.75, 4.56, 8.37];
  const titles = ["Diagnostic", "Personnalisation", "Pilotage classe"];
  const texts = [
    "Analyse les erreurs conceptuelles en temps reel (fractions, raisonnement, algebra).",
    "Genere des exercices graduels et des feedbacks adaptes au profil de chaque eleve.",
    "Affiche les risques de decrochage et propose des actions concretes avant le prochain controle.",
  ];
  const accents = ["D9E7FF", "DDF7F4", "EAF0FF"];

  for (let i = 0; i < 3; i += 1) {
    slide.addShape(pptx.ShapeType.roundRect, {
      x: cols[i],
      y: 2.2,
      w: 3.45,
      h: 4.8,
      rectRadius: 0.12,
      fill: { color: colors.white },
      line: { color: colors.gray300, pt: 1 },
    });
    slide.addShape(pptx.ShapeType.roundRect, {
      x: cols[i] + 0.22,
      y: 2.47,
      w: 1.28,
      h: 0.48,
      rectRadius: 0.08,
      fill: { color: accents[i] },
      line: { color: accents[i] },
    });
    slide.addText(`Etape ${i + 1}`, {
      x: cols[i] + 0.34,
      y: 2.61,
      w: 1.0,
      h: 0.2,
      fontFace: "Aptos",
      fontSize: 10,
      bold: true,
      color: colors.navy,
      align: "center",
    });

    slide.addText(titles[i], {
      ...calcBox(18, {
        x: cols[i] + 0.22,
        y: 3.12,
        w: 3.0,
        h: 0.78,
        valign: "top",
      }),
      fontFace: "Aptos Display",
      color: colors.navy,
      bold: true,
    });

    slide.addText(texts[i], {
      ...calcBox(12, {
        x: cols[i] + 0.22,
        y: 4.04,
        w: 3.0,
        h: 1.6,
        valign: "top",
      }),
      fontFace: "Aptos",
      color: colors.gray700,
    });

    slide.addText([
      { text: "Benefices:" },
      { text: "\nGain de temps prof" },
      { text: "\nMeilleure retention" },
      { text: "\nSuivi simple" },
    ], {
      x: cols[i] + 0.22,
      y: 5.78,
      w: 2.95,
      h: 1.05,
      fontFace: "Aptos",
      fontSize: 11,
      color: colors.gray700,
      bullet: { indentPt: 10 },
      breakLine: true,
    });
  }

  finalizeSlide(slide);
}

// Slide 4: marche
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Marche: une opportunite edtech B2B2C structurelle",
    "Priorite geographique: Suisse romande, France, Belgique francophone avant extension Europe."
  );

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72,
    y: 2.2,
    w: 6.05,
    h: 4.75,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
  });

  slide.addText("Taille de marche (estimation)", {
    x: 1.0,
    y: 2.44,
    w: 3.6,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 16,
    bold: true,
    color: colors.navy,
  });

  slide.addChart(pptx.ChartType.bar, [
    { name: "Valeur en MCHF", labels: ["TAM", "SAM", "SOM (3 ans)"], values: [1280, 260, 42] },
  ], {
    x: 1.0,
    y: 2.95,
    w: 5.5,
    h: 2.35,
    barDir: "col",
    chartColors: ["B9C4DE", "5FA0F5", "00A3A3"],
    valAxisMinVal: 0,
    valAxisMajorUnit: 200,
    catAxisLabelFontFace: "Aptos",
    valAxisLabelFontFace: "Aptos",
    showValue: true,
    showLegend: false,
    dataLabelSize: 10,
    dataLabelColor: colors.navy,
  });

  slide.addText("SOM cible base sur 1 500 etablissements equipes d’ici 2029.", {
    x: 1.0,
    y: 5.42,
    w: 5.55,
    h: 0.3,
    fontFace: "Aptos",
    fontSize: 10,
    color: colors.gray500,
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.03,
    y: 2.2,
    w: 5.56,
    h: 4.75,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
  });

  slide.addText("Pourquoi maintenant?", {
    x: 7.32,
    y: 2.44,
    w: 2.7,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 16,
    bold: true,
    color: colors.navy,
  });

  const nowBullets = [
    "Generalisation des equipements numeriques dans les classes secondaires.",
    "Pression institutionnelle sur les resultats STEM et l’equite de progression.",
    "Maturite des LLM pour un feedback pedagogique contextualise.",
    "Budget de remediations deja present dans les etablissements partenaires.",
  ];

  nowBullets.forEach((item, i) => {
    slide.addText(item, {
      ...calcBox(12, {
        x: 7.34,
        y: 2.98 + i * 0.78,
        w: 5.1,
        h: 0.66,
        valign: "top",
      }),
      fontFace: "Aptos",
      color: colors.gray700,
      bullet: { indentPt: 14 },
    });
  });

  finalizeSlide(slide);
}

// Slide 5: business model
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Modele economique: SaaS annualise et expansion par usage",
    "Un contrat etablissement + upsell familles + modules premium IA pour les reseaux scolaires."
  );

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.7,
    y: 2.2,
    w: 12.0,
    h: 4.74,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
  });

  const headers = ["Segment", "Offre", "Prix annuel", "Marge brute", "Part du CA 2026"];
  const rows = [
    ["Etablissement", "Licence plateforme + analytics", "18 kCHF", "83%", "54%"],
    ["Familles", "Abonnement eleve (B2C)", "120 CHF", "78%", "21%"],
    ["Reseaux", "Module pilotage multi-sites", "42 kCHF", "86%", "25%"],
  ];

  slide.addTable([headers, ...rows], {
    x: 0.95,
    y: 2.7,
    w: 11.5,
    h: 2.3,
    colW: [2.1, 3.9, 1.8, 1.6, 2.1],
    border: { type: "solid", pt: 1, color: colors.gray300 },
    fill: colors.white,
    fontFace: "Aptos",
    fontSize: 11,
    color: colors.gray700,
    valign: "middle",
    align: "left",
    autoFit: false,
    rowH: [0.5, 0.57, 0.57, 0.57],
  });

  slide.addShape(pptx.ShapeType.line, {
    x: 0.95,
    y: 3.2,
    w: 11.5,
    h: 0,
    line: { color: colors.gray300, pt: 1 },
  });

  slide.addText("CAC payback moyen: 8,5 mois | Retention annuelle brute: 92% | NRR cible: 122%", {
    x: 0.95,
    y: 5.35,
    w: 11.4,
    h: 0.3,
    fontFace: "Aptos",
    fontSize: 12,
    color: colors.navy,
    bold: true,
    align: "center",
  });

  slide.addChart(pptx.ChartType.line, [
    { name: "MRR (kCHF)", labels: ["T2", "T3", "T4", "T1-2026", "T2", "T3"], values: [32, 41, 49, 58, 66, 74] },
  ], {
    x: 1.0,
    y: 5.72,
    w: 11.2,
    h: 1.0,
    chartColors: ["2F80ED"],
    lineSize: 2,
    markerSize: 5,
    showLegend: false,
    valAxisMinVal: 20,
    valAxisMaxVal: 80,
    valAxisMajorUnit: 10,
    catAxisLabelSize: 9,
    valAxisLabelSize: 9,
  });

  finalizeSlide(slide);
}

// Slide 6: traction
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Traction: croissance saine et usage recurrent",
    "La valeur est tiree par l’usage hebdomadaire, pas uniquement par la signature commerciale."
  );

  addKpiCard(slide, 0.72, 2.26, 2.82, 1.42, "Eleves actifs hebdo", "8 900", "+63% vs an dernier", colors.green);
  addKpiCard(slide, 3.68, 2.26, 2.82, 1.42, "Exercices resolus/mois", "1,4 M", "+52% vs an dernier", colors.green);
  addKpiCard(slide, 6.64, 2.26, 2.82, 1.42, "Temps gagne prof", "3,1 h/sem", "mesure sur 22 ecoles", colors.cyan);
  addKpiCard(slide, 9.6, 2.26, 2.82, 1.42, "Churn logo", "5,8%", "en baisse continue", colors.green);

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72,
    y: 3.92,
    w: 6.22,
    h: 3.0,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
  });
  slide.addText("Usage hebdomadaire (en milliers de sessions)", {
    x: 0.98,
    y: 4.16,
    w: 4.1,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 14,
    bold: true,
    color: colors.navy,
  });

  slide.addChart(pptx.ChartType.line, [
    { name: "2025", labels: ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun"], values: [24, 27, 30, 34, 39, 44] },
    { name: "2026", labels: ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun"], values: [41, 47, 53, 58, 62, 67] },
  ], {
    x: 1.0,
    y: 4.56,
    w: 5.82,
    h: 2.08,
    chartColors: ["A7B6D8", "00A3A3"],
    showLegend: true,
    legendPos: "b",
    lineSize: 2,
    markerSize: 4,
    valAxisLabelSize: 9,
    catAxisLabelSize: 9,
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.16,
    y: 3.92,
    w: 5.26,
    h: 3.0,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
  });

  slide.addText("Pipeline commercial (12 mois)", {
    x: 7.42,
    y: 4.16,
    w: 3.8,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 14,
    bold: true,
    color: colors.navy,
  });

  slide.addChart(pptx.ChartType.doughnut, [
    { name: "Pipeline", labels: ["Signe", "Negociation", "Qualification"], values: [22, 31, 47] },
  ], {
    x: 7.52,
    y: 4.56,
    w: 2.52,
    h: 2.08,
    chartColors: ["2F80ED", "00A3A3", "D0D5DD"],
    showLegend: false,
    showPercent: true,
    dataLabelSize: 9,
  });

  slide.addText("84 etablissements qualifies\n31 en phase de negociation\n22 deja contractualises", {
    x: 10.18,
    y: 4.84,
    w: 2.1,
    h: 1.6,
    fontFace: "Aptos",
    fontSize: 11,
    color: colors.gray700,
    valign: "top",
  });

  finalizeSlide(slide);
}

// Slide 7: concurrence
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Concurrence: positionnement differencie et defensible",
    "Nous gagnons sur la personnalisation pedagogique locale et l’evidence d’impact."
  );

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72,
    y: 2.2,
    w: 12.0,
    h: 4.76,
    rectRadius: 0.08,
    fill: { color: colors.white },
    line: { color: colors.gray300, pt: 1 },
  });

  slide.addText("Comparatif simplifie", {
    x: 0.98,
    y: 2.45,
    w: 3.2,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 16,
    bold: true,
    color: colors.navy,
  });

  const compHeader = ["Critere", "Mathakine", "Plateformes LMS", "Apps B2C"];
  const compRows = [
    ["Personnalisation IA", "Fine et continue", "Limitee", "Elevee mais hors classe"],
    ["Vue enseignant", "Pilotage actionnable", "Reporting passif", "Quasi absente"],
    ["Integration etablissement", "Rapide (<2 semaines)", "Lourde", "Faible"],
    ["Preuve d’impact", "Mesuree par cohorte", "Variable", "Faible"],
    ["Barriere technologique", "Modele pedagogique proprietaire", "Faible", "Moyenne"],
  ];

  slide.addTable([compHeader, ...compRows], {
    x: 0.98,
    y: 2.9,
    w: 11.5,
    h: 2.95,
    colW: [2.8, 2.9, 2.9, 2.9],
    rowH: [0.5, 0.49, 0.49, 0.49, 0.49, 0.49],
    border: { type: "solid", pt: 1, color: colors.gray300 },
    fontFace: "Aptos",
    fontSize: 10,
    color: colors.gray700,
    valign: "middle",
    fill: colors.white,
    autoFit: false,
  });

  slide.addText("Moat principal: donnees d’apprentissage contextualisees + moteur de recommandations pedagogiques.", {
    ...calcBox(12, {
      x: 1.0,
      y: 6.08,
      w: 11.4,
      h: 0.58,
      valign: "top",
      bold: true,
    }),
    fontFace: "Aptos",
    color: colors.navy,
    align: "center",
  });

  finalizeSlide(slide);
}

// Slide 8: roadmap
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Roadmap 18 mois",
    "Execution focalisee sur produit, distribution et excellence operationnelle."
  );

  slide.addShape(pptx.ShapeType.line, {
    x: 1.0,
    y: 4.2,
    w: 11.3,
    h: 0,
    line: { color: colors.gray300, pt: 2 },
  });

  const milestones = [
    { x: 1.2, label: "Q2 2026", title: "Scale commercial", text: "40 nouvelles ecoles\n2 partenariats cantonaux", color: "2F80ED" },
    { x: 4.0, label: "Q4 2026", title: "Produit", text: "Moteur IA v2\nCoach enseignant en direct", color: "00A3A3" },
    { x: 6.8, label: "Q2 2027", title: "Expansion", text: "Lancement France\nCanal distributeurs", color: "2F80ED" },
    { x: 9.6, label: "Q4 2027", title: "Echelle", text: "250 etablissements\nEBITDA proche breakeven", color: "27AE60" },
  ];

  milestones.forEach((m, idx) => {
    const isTop = idx % 2 === 0;
    slide.addShape(pptx.ShapeType.ellipse, {
      x: m.x,
      y: 4.0,
      w: 0.36,
      h: 0.36,
      fill: { color: m.color },
      line: { color: m.color },
    });

    slide.addText(m.label, {
      x: m.x - 0.18,
      y: 4.44,
      w: 0.75,
      h: 0.2,
      fontFace: "Aptos",
      fontSize: 10,
      bold: true,
      color: colors.gray500,
      align: "center",
    });

    slide.addShape(pptx.ShapeType.roundRect, {
      x: m.x - 0.65,
      y: isTop ? 2.35 : 4.82,
      w: 1.68,
      h: 1.35,
      rectRadius: 0.08,
      fill: { color: colors.white },
      line: { color: colors.gray300, pt: 1 },
    });

    slide.addText(m.title, {
      x: m.x - 0.5,
      y: isTop ? 2.48 : 4.95,
      w: 1.38,
      h: 0.22,
      fontFace: "Aptos Display",
      fontSize: 12,
      bold: true,
      color: colors.navy,
      align: "center",
    });

    slide.addText(m.text, {
      x: m.x - 0.52,
      y: isTop ? 2.8 : 5.25,
      w: 1.42,
      h: 0.7,
      fontFace: "Aptos",
      fontSize: 9,
      color: colors.gray700,
      align: "center",
      valign: "top",
    });
  });

  finalizeSlide(slide);
}

// Slide 9: equipe
{
  const slide = pptx.addSlide();
  addBackground(
    slide,
    "Equipe fondatrice et gouvernance",
    "Une equipe hybride education, IA et execution commerciale SaaS."
  );

  const members = [
    { name: "CEO", role: "Ex-Head of Product edtech\n10 ans dans le scale-up SaaS", x: 0.88 },
    { name: "CTO", role: "PhD IA appliquee\nex-lead ML plateforme education", x: 4.08 },
    { name: "CPO", role: "Ancienne enseignante\nspecialiste parcours pedagogiques", x: 7.28 },
    { name: "Advisor", role: "Ex-DG groupe scolaire\nacces aux reseaux institutionnels", x: 10.48 },
  ];

  members.forEach((m) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x: m.x,
      y: 2.35,
      w: 2.5,
      h: 4.35,
      rectRadius: 0.08,
      fill: { color: colors.white },
      line: { color: colors.gray300, pt: 1 },
    });

    slide.addShape(pptx.ShapeType.ellipse, {
      x: m.x + 0.84,
      y: 2.72,
      w: 0.82,
      h: 0.82,
      fill: { color: "DCE6FA" },
      line: { color: "B5C7EC", pt: 1 },
    });

    slide.addText(m.name, {
      x: m.x + 0.25,
      y: 3.75,
      w: 2.0,
      h: 0.28,
      fontFace: "Aptos Display",
      fontSize: 15,
      bold: true,
      color: colors.navy,
      align: "center",
    });

    slide.addText(m.role, {
      ...calcBox(11, {
        x: m.x + 0.22,
        y: 4.2,
        w: 2.06,
        h: 1.45,
        valign: "top",
      }),
      fontFace: "Aptos",
      color: colors.gray700,
      align: "center",
    });

    slide.addShape(pptx.ShapeType.roundRect, {
      x: m.x + 0.33,
      y: 5.87,
      w: 1.84,
      h: 0.42,
      rectRadius: 0.08,
      fill: { color: "ECFDF3" },
      line: { color: "B7E7C8", pt: 1 },
    });

    slide.addText("Equipe completee", {
      x: m.x + 0.44,
      y: 5.99,
      w: 1.62,
      h: 0.2,
      fontFace: "Aptos",
      fontSize: 9,
      color: colors.green,
      bold: true,
      align: "center",
    });
  });

  finalizeSlide(slide);
}

// Slide 10: demande d'investissement
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.navy };

  slide.addText("Demande d’investissement", {
    x: 0.9,
    y: 0.96,
    w: 7.0,
    h: 0.6,
    fontFace: "Aptos Display",
    fontSize: 36,
    bold: true,
    color: colors.white,
  });

  slide.addText("Seed round: 1,8 MCHF pour 18 mois d’acceleration", {
    x: 0.92,
    y: 1.78,
    w: 8.0,
    h: 0.36,
    fontFace: "Aptos",
    fontSize: 16,
    color: "8BDCDC",
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.92,
    y: 2.5,
    w: 6.9,
    h: 3.9,
    rectRadius: 0.1,
    fill: { color: "17315F" },
    line: { color: "2A4D8F", pt: 1 },
  });

  const uses = [
    "45% Produit & IA (personnalisation, analytics, securite)",
    "30% Go-to-market (sales, partenariats institutionnels)",
    "15% Operations & support ecoles",
    "10% Reserve strategique",
  ];
  uses.forEach((u, i) => {
    slide.addText(u, {
      ...calcBox(13, {
        x: 1.24,
        y: 2.94 + i * 0.76,
        w: 6.28,
        h: 0.55,
        valign: "top",
      }),
      fontFace: "Aptos",
      color: "EAF2FF",
      bullet: { indentPt: 15 },
    });
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.18,
    y: 2.5,
    w: 4.2,
    h: 3.9,
    rectRadius: 0.1,
    fill: { color: "11284F" },
    line: { color: "2A4D8F", pt: 1 },
  });

  slide.addText("Objectifs fin 2027", {
    x: 8.45,
    y: 2.8,
    w: 3.66,
    h: 0.3,
    fontFace: "Aptos Display",
    fontSize: 16,
    bold: true,
    color: colors.white,
  });

  slide.addText("250 etablissements\n40 000 eleves actifs/mois\nARR > 4,5 MCHF\nChemin clair vers la rentabilite", {
    x: 8.45,
    y: 3.28,
    w: 3.55,
    h: 1.7,
    fontFace: "Aptos",
    fontSize: 13,
    color: "D5E3FF",
    valign: "top",
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.45,
    y: 5.33,
    w: 2.9,
    h: 0.56,
    rectRadius: 0.08,
    fill: { color: colors.cyan },
    line: { color: colors.cyan },
  });

  slide.addText("Contact: founders@mathakine.com", {
    x: 8.57,
    y: 5.51,
    w: 2.64,
    h: 0.2,
    fontFace: "Aptos",
    fontSize: 11,
    bold: true,
    color: colors.navy,
    align: "center",
  });

  finalizeSlide(slide);
}

const outputPath = path.join(__dirname, "Mathakine_Deck_Investisseurs_FR.pptx");
pptx.writeFile({ fileName: outputPath });
console.log(`Deck genere: ${outputPath}`);

