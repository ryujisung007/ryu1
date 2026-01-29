# =========================
# Top5 가로 막대그래프
# =========================
import matplotlib.pyplot as plt

FLAVOR_EN_SIMPLE = {
    "오렌지": "Orange",
    "사과": "Apple",
    "포도": "Grape",
    "망고": "Mango",
    "레몬": "Lemon",
    "자몽": "Grapefruit",
    "복숭아": "Peach",
    "파인애플": "Pineapple",
    "딸기": "Strawberry",
    "블루베리": "Blueberry",
    "유자": "Yuzu",
    "배": "Pear",
}

def render_top5_barh(top5):
    flavors = [FLAVOR_EN_SIMPLE[t["flavor"]] for t in top5]
    shares = [t["share"] for t in top5]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(flavors, shares)
    ax.invert_yaxis()
    ax.set_xlabel("Share (%)")
    ax.set_title("Top5 Flavor Share")

    st.pyplot(fig, clear_figure=True)

# =========================
# Sensory Radar (축소 + 기준 비교)
# =========================
import numpy as np

SENSORY_AXES = ["Sweet", "Acid", "Body", "Fresh", "Finish"]
SENSORY_BASE = [3, 3, 3, 3, 3]
SENSORY_AI_A = [2, 4, 3, 4, 3]

def render_sensory_radar():
    labels = SENSORY_AXES
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles = np.concatenate([angles, [angles[0]]])

    base = SENSORY_BASE + [SENSORY_BASE[0]]
    ai = SENSORY_AI_A + [SENSORY_AI_A[0]]

    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_subplot(111, polar=True)

    ax.plot(angles, base, label="Base Formula")
    ax.fill(angles, base, alpha=0.1)

    ax.plot(angles, ai, label="AI(A) Target")
    ax.fill(angles, ai, alpha=0.15)

    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels)
    ax.set_ylim(0, 5)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    st.pyplot(fig, clear_figure=True)

# =========================
# AI 미션 생성 (문제만 생성)
# =========================
def generate_ai_mission(role, flavor):
    try:
        from openai import OpenAI
        client = OpenAI()

        prompt = f"""
너는 식품회사 신입사원 교육용 문제 출제자다.

직무: {role}
플레이버: {flavor}

요구사항:
- 객관식 문제 1개
- 보기 3개
- 정답 명확
- 제조공정/배합/품질 중 하나 포함
- JSON만 출력

형식:
{{
  "type": "...",
  "question": "...",
  "options": ["...", "...", "..."],
  "answer_index": 0,
  "explanation": "..."
}}
"""
        resp = client.responses.create(model="o4-mini", input=prompt)
        return json.loads(resp.output_text)

    except Exception:
        # fallback
        return {
            "type": "제조공정",
            "question": "과즙 음료 제조 시 가장 적절한 공정 순서는?",
            "options": [
                "원료계량 → 혼합 → 살균 → 충전",
                "원료계량 → 살균 → 혼합 → 충전",
                "혼합 → 충전 → 살균"
            ],
            "answer_index": 0,
            "explanation": "혼합 후 살균해야 기억질화와 미생물 안정성을 동시에 확보할 수 있다."
        }

# =========================
# 미션 UI
# =========================
st.subheader("🎯 AI 생성 미션")

role = st.selectbox("직무 선택", ["A.기획", "B.마케팅", "C.연구개발"])
if st.button("AI 미션 생성"):
    st.session_state.mission = generate_ai_mission(role, st.session_state.selected_flavor)

m = st.session_state.get("mission")
if m:
    st.markdown(f"**[{m['type']}] {m['question']}**")
    ans = st.radio("정답 선택", m["options"])
    if st.button("제출"):
        if ans == m["options"][m["answer_index"]]:
            st.success("정답입니다")
        else:
            st.error("오답입니다")
        st.info(m["explanation"])
