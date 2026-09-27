import type { NextConfig } from "next";

const qLoveSite = "https://olove-research.kangbs2486.chatgpt.site";

const researchRedirects = [
  ["/research/a-systematic-review-of-the-biological-effects-of-2021-34641429", "/paper/cordycepin-systematic-review"],
  ["/research/an-immunomodulatory-mushroom-cordyceps-militaris-2026-41432716", "/paper/cordyceps-immunomodulatory-review"],
  ["/research/anti-inflammatory-effects-of-cordycepin-a-review-2020-33090621", "/evidence/reviews"],
  ["/research/beneficial-effect-of-cordyceps-militaris-on-exer-2020-33312018", "/paper/cordyceps-cellular-energy-exercise"],
  ["/research/cordycepin-3-deoxyadenosine-attenuates-age-relat-2012-23000874", "/evidence/preclinical-studies"],
  ["/research/cordycepin-combined-with-antioxidant-effects-imp-2025-40059099", "/paper/cordycepin-antioxidant-fatigue"],
  ["/research/cordycepin-exhibits-anti-fatigue-effect-via-acti-2022-36399798", "/paper/cordycepin-fatigue-pathway"],
  ["/research/cordycepin-for-health-and-wellbeing-a-potent-bio-2020-32545666", "/evidence/reviews"],
  ["/research/cordycepin-protects-renal-ischemia-reperfusion-i-2020-31951250", "/evidence/preclinical-studies"],
  ["/research/cordyceps-militaris-reduces-oxidative-stress-and-2022-36009221", "/evidence/preclinical-studies"],
  ["/research/cordyceps-polysaccharides-a-review-of-their-immu-2024-39519748", "/paper/cordyceps-polysaccharides-review"],
  ["/research/current-evidence-of-ergogenic-and-post-exercise--2026-41829950", "/paper/cordyceps-exercise-recovery-review"],
  ["/research/immunomodulation-and-protective-effects-of-cordy-2024-39590481", "/paper/cordyceps-infection-model"],
  ["/research/inhibitory-effects-of-cordycepin-3-deoxyadenosin-2007-18051324", "/evidence/preclinical-studies"],
  ["/research/lipid-lowering-effect-of-cordycepin-3-deoxyadeno-2011-21882527", "/evidence/preclinical-studies"],
  ["/research/protective-effects-of-cordycepin-against-d-galac-2022-35352454", "/evidence/preclinical-studies"],
  ["/research/the-protective-effect-of-cordycepin-on-d-galacto-2017-28522898", "/evidence/preclinical-studies"],
  ["/research/trends-in-the-immunomodulatory-effects-of-cordyc-2020-33328984", "/evidence/reviews"],
] as const;

const nextConfig: NextConfig = {
  async redirects() {
    return [
      {
        source: "/research",
        destination: `${qLoveSite}/evidence`,
        permanent: true,
      },
      ...researchRedirects.map(([source, destination]) => ({
        source,
        destination: `${qLoveSite}${destination}`,
        permanent: true,
      })),
      {
        source: "/research/:path*",
        destination: `${qLoveSite}/evidence`,
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
