# testapp/views.py
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

# ⬇︎ api_print 에 필요한 추가 import
import os
import subprocess
import sys
from django.http import JsonResponse
from django.conf import settings

# 결과 매핑 (조합 -> type_XX)
COMBINATION_MAP = {
    "AAAAAA": "type_01",
    "AAAAAB": "type_02",
    "AAAABB": "type_03",
    "AAABBB": "type_04",
    "AABBBB": "type_05",
    "ABBBBB": "type_06",
    "BBBBBB": "type_07",
    "BBBBBC": "type_08",
    "BBBBCC": "type_09",
    "BBBCCC": "type_10",
    "BBCCCC": "type_11",
    "BCCCCC": "type_12",
}

# -------- 공통 유틸 --------
def _compute_result_type(answers):
    """
    6개 답변(문자 리스트)을 받아 'type_XX'를 반환.
    유효하지 않으면 기본값 'type_01'로 폴백.
    """
    if len(answers) != 6:
        return "type_01", True  # (값, is_fallback)
    code = "".join(answers)
    result_type = COMBINATION_MAP.get(code)
    if not result_type:
        return "type_01", True
    return result_type, False


def _go_prev(request, keep_len, prev_name):
    """
    '이전으로' 버튼 공통 처리: 현재까지 answers에서 keep_len까지만 유지 후 이전 화면으로 이동
    """
    answers = request.session.get("answers", [])
    answers = answers[:keep_len]
    request.session["answers"] = answers
    return redirect(prev_name)


# -------- 페이지 핸들러 --------
def home(request):
    return render(request, "home.html")


def question_1(request):
    if request.method == "POST":
        answer = request.POST.get("answer")
        # q1은 되돌리기 없음 → 새로운 시작
        request.session["answers"] = [answer] if answer else []
        return redirect("question_2")
    return render(request, "question_1.html")


def question_2(request):
    if request.method == "POST":
        if request.POST.get("nav") == "prev":
            return _go_prev(request, keep_len=0, prev_name="question_1")

        answer = request.POST.get("answer")
        answers = request.session.get("answers", [])[:1]
        if answer:
            answers.append(answer)
        request.session["answers"] = answers
        return redirect("question_3")
    return render(request, "question_2.html")


def question_3(request):
    if request.method == "POST":
        if request.POST.get("nav") == "prev":
            return _go_prev(request, keep_len=1, prev_name="question_2")

        answer = request.POST.get("answer")
        answers = request.session.get("answers", [])[:2]
        if answer:
            answers.append(answer)
        request.session["answers"] = answers
        return redirect("question_4")
    return render(request, "question_3.html")


def question_4(request):
    if request.method == "POST":
        if request.POST.get("nav") == "prev":
            return _go_prev(request, keep_len=2, prev_name="question_3")

        answer = request.POST.get("answer")
        answers = request.session.get("answers", [])[:3]
        if answer:
            answers.append(answer)
        request.session["answers"] = answers
        return redirect("question_5")
    return render(request, "question_4.html")


def question_5(request):
    if request.method == "POST":
        if request.POST.get("nav") == "prev":
            return _go_prev(request, keep_len=3, prev_name="question_4")

        answer = request.POST.get("answer")
        answers = request.session.get("answers", [])[:4]
        if answer:
            answers.append(answer)
        request.session["answers"] = answers
        return redirect("question_6")
    return render(request, "question_5.html")


def question_6(request):
    if request.method == "POST":
        if request.POST.get("nav") == "prev":
            return _go_prev(request, keep_len=4, prev_name="question_5")

        answer = request.POST.get("answer")
        answers = request.session.get("answers", [])[:5]
        if answer:
            answers.append(answer)
        request.session["answers"] = answers
        return redirect("result")
    return render(request, "question_6.html")


def result(request):
    """
    최종 결과 페이지
    - result_type: 'type_01' ~ 'type_12'
    - img_path: 화면용 정적 파일 경로 (characters/type_XX.PNG)
    - print_path: 인쇄용 정적 파일 경로 (characters/type_XX_result.png)
    """
    answers = request.session.get("answers", [])
    result_type, is_fallback = _compute_result_type(answers)

    # ✅ 템플릿에서 바로 쓸 수 있게 경로까지 만들어서 넘김
    img_base = result_type  # 예: "type_01"
    img_path = f"characters/{img_base}.PNG"
    print_path = f"characters/{img_base}_result.png"

    context = {
        "result_type": result_type,
        "img_base": img_base,
        "img_path": img_path,         # 화면용 파일 경로
        "print_path": print_path,     # 인쇄용 파일 경로
        "is_fallback": is_fallback,
    }
    return render(request, "result.html", context)


@require_POST
def reset(request):
    # 세션 전체 초기화 후 첫 화면으로
    request.session.flush()
    return redirect("home")


# ---------- 라벨기 직접 출력 API ----------
@require_POST
def api_print(request):
    """
    클라이언트에서 'img_rel' (예: "characters/type_01_result.png") 을 받아
    서버에서 CUPS(lp)로 바로 인쇄합니다.

    settings.DIRECT_PRINT == False 이면 실제 인쇄는 하지 않고 메시지로만 응답합니다.
    """
    try:
        img_rel = request.POST.get("img_rel")
        if not img_rel:
            return JsonResponse({"error": "img_rel 파라미터가 없습니다."}, status=400)

        # static 실제 경로로 변환 (보안: static 폴더 밖 접근 금지)
        static_root = os.path.join(settings.BASE_DIR, "testapp", "static")
        full_path = os.path.normpath(os.path.join(static_root, img_rel))

        # 디렉터리 탈출 방지
        if not os.path.abspath(full_path).startswith(os.path.abspath(static_root)):
            return JsonResponse({"error": "잘못된 경로입니다."}, status=400)

        if not os.path.exists(full_path):
            return JsonResponse({"error": f"파일이 없습니다: {img_rel}"}, status=404)

        # 개발 모드면 실제 인쇄는 건너뜀
        if not getattr(settings, "DIRECT_PRINT", False):
            return JsonResponse({"message": f"(개발 모드) 인쇄했을 파일: {img_rel}"})

        # 운영: CUPS(lp)로 직접 인쇄
        printer = getattr(settings, "LABEL_PRINTER_NAME", None)
        media = getattr(settings, "LABEL_MEDIA", None)

        if not printer:
            return JsonResponse({"error": "LABEL_PRINTER_NAME 미설정"}, status=500)

        # macOS/Linux 에서만 lp 사용 가능 (Windows면 안내)
        if sys.platform.startswith("win"):
            return JsonResponse({"error": "Windows 환경에서는 CUPS(lp) 직접 인쇄를 사용할 수 없습니다."}, status=500)

        cmd = ["lp", "-d", printer]
        if media:
            cmd += ["-o", f"media={media}"]
        # 필요 시 옵션을 조정하세요.
        cmd += [
            "-o", "fit-to-page",      # 라벨 박스에 맞춤
            "-o", "position=center",  # 중앙 정렬
            full_path
        ]

        try:
            subprocess.run(cmd, check=True)
            return JsonResponse({"message": f"인쇄 요청 완료: {img_rel}"})
        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": f"인쇄 실패: {e}"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
