from flask import render_template, request, redirect, session, send_from_directory
from datetime import datetime, timedelta
from utils import check_empty
import services.candidates as candidate_service
import services.positions as position_service

def add_candidate(position_id):
    if request.method == 'POST':
        result = candidate_service.add(position_id, request.form['first_name'], request.form['last_name'], request.form['email'])
        if result['success']:
            return redirect(f'/positions/{position_id}')
        else:
            return render_template('add_candidate.html', **result['error'], avatar=session['avatar'])
    else:
        return render_template('add_candidate.html', avatar=session['avatar'])

def candidate(position_id, candidate_id):
    if request.method == 'POST':
        if 'form_reject_reason' in request.form:
            reject_reason = request.form['reject_reason']
            result = candidate_service.update_reject_reason(candidate_id, reject_reason)
        elif 'form_decline_reason' in request.form:
            decline_reason = request.form['decline_reason']
            result = candidate_service.update_decline_reason(candidate_id, decline_reason)
        else:
            return redirect(f'/positions/{position_id}/{candidate_id}')
        if result['success']:
            return redirect(f'/positions/{position_id}/{candidate_id}')
        else:
            cand = candidate_service.get(candidate_id)
            return render_template('candidate.html', **result['error'], **cand, avatar=session['avatar'])
    else:
        result = candidate_service.get(candidate_id)
        if request.args.get('error') is not None:
            return render_template('candidate.html', **result, error=True, avatar=session['avatar'])
        return render_template('candidate.html', **result, avatar=session['avatar'])

def delete_candidate(position_id, candidate_id):
    result = candidate_service.delete(candidate_id)
    if result['success']:
        return redirect(f'/positions/{position_id}')

def add_cv():
    if request.method == 'POST':
        cand_id = request.form['candidate']
        if 'cv' in request.files:
            result = candidate_service.add_cv(cand_id, request.files['cv'])
            if result['success']:
                return render_template('add_cv.html', **result['arguments'], avatar=session['avatar'])
        else:
            result = candidate_service.update(cand_id, request.form['email'], request.form['phone'], request.form['address'], request.form['postal_code'], request.form['city'], request.form['country'], request.form['birthdate'])
            if result['success']:
                return redirect(f'/positions/{result["pos_id"]}/{cand_id}')
        candidates = candidate_service.get_all()
        return render_template('add_cv.html', **result['error'], candidates=candidates, avatar=session['avatar'])
    else:
        cand = request.args.get('cand')
        if cand is None:
            candidates = candidate_service.get_all()
            return render_template('add_cv.html', candidates=candidates, avatar=session['avatar'])
        else:
            try:
                candidate = candidate_service.get(cand)['candidate']
            except:
                return redirect('/add_cv')
            return render_template('add_cv.html', candidate=candidate, avatar=session['avatar'])

def add_ml():
    if request.method == 'POST':
        cand_id = request.form['candidate']
        result = candidate_service.add_ml(cand_id, request.files['ml'])
        if result['success']:
            return redirect(f'/positions/{result["pos_id"]}/{cand_id}')
        else:
            candidates = candidate_service.get_all()
            return render_template('add_ml.html', **result['error'], candidates=candidates, avatar=session['avatar'])
    else:
        cand = request.args.get('cand')
        if cand is None:
            candidates = candidate_service.get_all()
            return render_template('add_ml.html', candidates=candidates, avatar=session['avatar'])
        else:
            try:
                candidate = candidate_service.get(cand)['candidate']
            except:
                return redirect('/add_ml')
            return render_template('add_ml.html', candidate=candidate, avatar=session['avatar'])

def view_cv(position_id, candidate_id):
    result = candidate_service.view_cv(position_id, candidate_id)
    if result['success']:
        return send_from_directory(f"uploads/{position_id}/{candidate_id}", result['filename'])
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}')

def view_ml(position_id, candidate_id):
    result = candidate_service.view_ml(position_id, candidate_id)
    if result['success']:
        return send_from_directory(f"uploads/{position_id}/{candidate_id}", result['filename'])
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}')

def delete_cv(position_id, candidate_id):
    candidate_service.delete_cv(position_id, candidate_id)
    return redirect(f'/positions/{position_id}/{candidate_id}')

def delete_ml(position_id, candidate_id):
    candidate_service.delete_ml(position_id, candidate_id)
    return redirect(f'/positions/{position_id}/{candidate_id}')

def interview_invitation(position_id, candidate_id):
    result = candidate_service.interview_invitation(position_id, candidate_id, session['user_id'])
    return render_template('response_positive.html', **result, avatar=session['avatar'])

def rejection_email(position_id, candidate_id):
    result = candidate_service.rejection_email(position_id, candidate_id, session['user_id'])
    return render_template('response_negative.html', **result, avatar=session['avatar'])

def rejection_email_with_reasons(position_id, candidate_id):
    result = candidate_service.rejection_email_with_reasons(position_id, candidate_id, session['user_id'])
    return render_template('response_negative.html', **result, avatar=session['avatar'])

def add_interview(position_id, candidate_id):
    if request.method == 'POST':
        score = request.form['score']
        notes = request.form['notes']
        date = request.form['date']
        result = candidate_service.add_interview(candidate_id, position_id, score, notes, date)
        if result['success']:
            return redirect(f'/positions/{position_id}/{candidate_id}')
        else:
            candidate = candidate_service.get(candidate_id)['candidate']
            position = position_service.get(position_id)
            return render_template('interview.html', **result['error'], candidate=candidate, position=position, avatar=session['avatar'])
    else:
        candidate = candidate_service.get(candidate_id)['candidate']
        position = position_service.get(position_id)
        return render_template('interview.html', candidate=candidate, position=position, avatar=session['avatar'])

def edit_interview(position_id, candidate_id):
    if request.method == 'POST':
        score = request.form['score']
        notes = request.form['notes']
        date = request.form['date']
        result = candidate_service.edit_interview(candidate_id, score, notes, date)
        if result['success']:
            return redirect(f'/positions/{position_id}/{candidate_id}')
        else:
            candidate = candidate_service.get(candidate_id)['candidate']
            position = position_service.get(position_id)
            interview = candidate_service.get(candidate_id)['interview']
            return render_template('interview.html', **result['error'], candidate=candidate, position=position, interview=interview, avatar=session['avatar'])
    else:
        candidate = candidate_service.get(candidate_id)['candidate']
        position = position_service.get(position_id)
        interview = candidate_service.get(candidate_id)['interview']
        if interview is None:
            return redirect(f'/positions/{position_id}/{candidate_id}/add_interview')
        return render_template('interview.html', candidate=candidate, position=position, interview=interview, avatar=session['avatar'])

def mark_invited(position_id, candidate_id):
    result = candidate_service.mark_invited(candidate_id)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def unmark_invited(position_id, candidate_id):
    result = candidate_service.unmark_invited(candidate_id)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def mark_offer(position_id, candidate_id):
    result = candidate_service.mark_offer(candidate_id)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def unmark_offer(position_id, candidate_id):
    result = candidate_service.unmark_offer(candidate_id)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def mark_hired(position_id, candidate_id):
    result = candidate_service.mark_hired(candidate_id)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def unmark_hired(position_id, candidate_id):
    result = candidate_service.unmark_hired(candidate_id)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def remove_reject_reason(position_id, candidate_id):
    result = candidate_service.update_reject_reason(candidate_id, None)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def remove_decline_reason(position_id, candidate_id):
    result = candidate_service.update_decline_reason(candidate_id, None)
    if result['success']:
        return redirect(f'/positions/{position_id}/{candidate_id}')
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}?error=true')

def stats():
    if request.method == 'POST':
        date_from = request.form['date_from']
        date_to = request.form['date_to']
        result = candidate_service.stats(date_from, date_to)
        return render_template('stats.html', **result, avatar=session['avatar'])
    else:
        result = candidate_service.stats(datetime.now().date() - timedelta(days=30), datetime.now().date())
        return render_template('stats.html', **result, avatar=session['avatar'])

def search():
    if request.method == 'POST':
        name = check_empty(request.form['name'])
        email = check_empty(request.form['email'])
        result = candidate_service.search(name, email)
        if result['success']:
            return render_template('search.html', result=result['result'], avatar=session['avatar'])
        else:
            return redirect('/search')
    else:
        return render_template('search.html', avatar=session['avatar'])
