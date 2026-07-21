# 컴플라이언스 가이드 — 제왕충초 담금주 × 코디세핀 근거

이 문서는 **법적 자문이 아닙니다.** 마케팅·라벨 문구 확정 전 법무/규제 담당자 검토가 필요합니다.

## 제품 성격

- 큐사랑 **제왕충초 담금주**는 **주류**입니다.
- **건강기능식품(HFF)**이 아닙니다.
- 논문·FDA·식약처 자료를 “효능 근거”로 광고에 붙이는 것은 고위험입니다.

## 대한민국

### 주류 광고
- 국민건강증진법 등에 따라 음주가 **체력·운동능력·질병 치료·정신건강**에 도움이 된다는 식의 표현은 금지됩니다.
- “코디세핀이 ~을 치료/예방한다”류 문구는 주류 광고에 사용하지 않습니다.

### 건강기능식품
- *Cordyceps militaris* 추출물 등 고시 원료의 **면역 기능** 등 인정 문구는 **HFF 제품**에만 해당합니다.
- 담금주가 HFF가 아니면 고시 클레임을 **라벨·광고에 전용하지 않습니다** (`KR_HFF_ref_only`).

### 일반식품·한약 암시
- 일반식품에 한약/건강기능식품과 유사한 효능 표시를 하는 것은 식약처 단속 대상이 될 수 있습니다.

## 미국 FDA (참고)

- Cordycepin/*Cordyceps*는 일반적으로 **승인된 의약품 적응증이 없습니다**.
- Dietary supplement로 유통되는 경우 **structure/function claim**만 가능하며, 질병 치료·예방·진단 클레임은 **미승인 신약**으로 취급될 수 있습니다.
- Warning letter에서 Cordyceps 제품이 **질병 클레임**으로 지적된 사례가 있습니다.
- **“FDA approved”**를 코디세핀/동충하초 효능에 붙이지 않습니다.

## 근거 등급과 광고

| evidence_strength | 의미 | 소비자 광고 |
|-------------------|------|-------------|
| A (human RCT) | 인간 RCT | 주류에서는 여전히 효능 표현 금지. 객관 “연구 존재” 서술만 법무 승인 후 |
| B | limited human | 내부/교육 우선 |
| C | animal | research_only |
| D | in vitro | research_only |
| E | traditional | 역사적 맥락만, 효능 입증으로 쓰지 않음 |
| F | review / unclear | 합성 참고 |

## 파이프라인 강제 규칙

1. 질병어 감지 → `risk_flags: disease_language`, `needs_legal_review`
2. 종 불일치 (*sinensis*/Cs-4 vs militaris) → `species_mismatch`, relevance=`extrapolated`
3. in vitro/animal → 기본 `maps_to_market=research_only`
4. `marketing_safe` export = `citation_status=approved` **AND** `maps_to_market=KR_liquor_context` 만

## 허용되는 톤 예시 (법무 승인 전제)

- “코디세핀(cordycepin)은 *Cordyceps*속 균류에서 연구되는 성분입니다.”
- “관련 연구가 학술 문헌에 보고되어 있습니다. (질병 치료 효과와는 무관)”

## 금지 톤 예시

- “암세포를 죽인다 / 항암 효과”
- “식약처가 효능을 인정한 담금주”
- “FDA 승인 성분”
- “면역력 증진 / 피로 회복 보장”
