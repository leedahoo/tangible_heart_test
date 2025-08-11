# testapp/views.py
from django.shortcuts import render, redirect

# 예시 매핑 7종
COMBINATION_MAP = {
    "AAAAAA": "type_01",
    "AAAAAB": "type_02",
    "AAAABB": "type_03",
    "AAABBB": "type_04",
    "AABBBB": "type_05",
    "ABBBBB": "type_06",
}

def home(request):
    return render(request, 'home.html')


# 공통 헬퍼: 이전으로 버튼 처리
def _go_prev(request, keep_len, prev_name):
    answers = request.session.get('answers', [])
    answers = answers[:keep_len]   # keep_len개만 유지 (한 단계 되돌림)
    request.session['answers'] = answers
    return redirect(prev_name)


def question_1(request):
    if request.method == 'POST':
        # q1은 뒤로가기 버튼 없음
        answer = request.POST.get('answer')
        request.session['answers'] = [answer]
        return redirect('question_2')
    return render(request, 'question_1.html')


def question_2(request):
    if request.method == 'POST':
        # 뒤로가기
        if request.POST.get('nav') == 'prev':
            return _go_prev(request, keep_len=0, prev_name='question_1')
        # 정방향
        answer = request.POST.get('answer')
        answers = request.session.get('answers', [])
        answers = answers[:1]
        answers.append(answer)
        request.session['answers'] = answers
        return redirect('question_3')
    return render(request, 'question_2.html')


def question_3(request):
    if request.method == 'POST':
        if request.POST.get('nav') == 'prev':
            return _go_prev(request, keep_len=1, prev_name='question_2')
        answer = request.POST.get('answer')
        answers = request.session.get('answers', [])
        answers = answers[:2]
        answers.append(answer)
        request.session['answers'] = answers
        return redirect('question_4')
    return render(request, 'question_3.html')


def question_4(request):
    if request.method == 'POST':
        if request.POST.get('nav') == 'prev':
            return _go_prev(request, keep_len=2, prev_name='question_3')
        answer = request.POST.get('answer')
        answers = request.session.get('answers', [])
        answers = answers[:3]
        answers.append(answer)
        request.session['answers'] = answers
        return redirect('question_5')
    return render(request, 'question_4.html')


def question_5(request):
    if request.method == 'POST':
        if request.POST.get('nav') == 'prev':
            return _go_prev(request, keep_len=3, prev_name='question_4')
        answer = request.POST.get('answer')
        answers = request.session.get('answers', [])
        answers = answers[:4]
        answers.append(answer)
        request.session['answers'] = answers
        return redirect('question_6')
    return render(request, 'question_5.html')


def question_6(request):
    if request.method == 'POST':
        if request.POST.get('nav') == 'prev':
            return _go_prev(request, keep_len=4, prev_name='question_5')
        answer = request.POST.get('answer')
        answers = request.session.get('answers', [])
        answers = answers[:5]
        answers.append(answer)
        request.session['answers'] = answers
        return redirect('result')
    return render(request, 'question_6.html')


def result(request):
    answers = request.session.get('answers', [])
    if len(answers) != 6:
        result_type = 'unknown'
    else:
        answer_code = ''.join(answers)
        result_type = COMBINATION_MAP.get(answer_code, 'unknown')
    return render(request, 'result.html', {'result_type': result_type})

from django.views.decorators.http import require_POST

@require_POST
def reset(request):
    request.session.flush()   # 세션 전체 초기화
    return redirect('home')
