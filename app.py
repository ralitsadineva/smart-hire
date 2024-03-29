from flask import Flask, render_template, request, redirect, session
from controllers.users import login, signup, googleCallback, logout, change_password, home, profile
from controllers.positions import positions, add_position, duplicate_position, positions_history, position, edit_position, archive_position, activate_position
from controllers.candidates import add_candidate, candidate, delete_candidate, add_cv, add_ml, view_cv, view_ml, delete_cv, delete_ml, interview_invitation, rejection_email, rejection_email_with_reasons, add_interview, edit_interview, mark_invited, unmark_invited, mark_offer, unmark_offer, mark_hired, unmark_hired, remove_reject_reason, remove_decline_reason, stats, search
import secrets
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

EXCLUDED_ROUTES = ['/', '/login', '/signup', '/signin-google', '/logout']

@app.before_request
def check_session():
    if request.path not in EXCLUDED_ROUTES and 'username' not in session and not request.path.startswith('/static'):
        return redirect('/')

@app.route('/')
def index():
    return render_template('index.html', landing_page=True)

app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/signup', 'signup', signup, methods=['GET', 'POST'])
app.add_url_rule('/signin-google', 'googleCallback', googleCallback, methods=['POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/change_password', 'change_password', change_password, methods=['GET', 'POST'])
app.add_url_rule('/home', 'home', home)
app.add_url_rule('/profile', 'profile', profile, methods=['GET', 'POST'])

app.add_url_rule('/positions', 'positions', positions)
app.add_url_rule('/positions/add', 'add_position', add_position, methods=['GET', 'POST'])
app.add_url_rule('/positions/add/<string:position_id>', 'duplicate_position', duplicate_position, methods=['GET', 'POST'])
app.add_url_rule('/positions/history', 'positions_history', positions_history)
app.add_url_rule('/positions/<string:position_id>', 'position', position)
app.add_url_rule('/positions/<string:position_id>/edit', 'edit_position', edit_position, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/archive', 'archive_position', archive_position)
app.add_url_rule('/positions/<string:position_id>/activate', 'activate_position', activate_position)

app.add_url_rule('/positions/<string:position_id>/add_candidate', 'add_candidate', add_candidate, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>', 'candidate', candidate, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/delete', 'delete_candidate', delete_candidate)
app.add_url_rule('/add_cv', 'add_cv', add_cv, methods=['GET', 'POST'])
app.add_url_rule('/add_ml', 'add_ml', add_ml, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/view_cv', 'view_cv', view_cv)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/view_ml', 'view_ml', view_ml)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/del_cv', 'delete_cv', delete_cv)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/del_ml', 'delete_ml', delete_ml)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/invitation', 'interview_invitation', interview_invitation)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/rejection', 'rejection_email', rejection_email)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/rejection_with_reasons', 'rejection_email_with_reasons', rejection_email_with_reasons)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/add_interview', 'add_interview', add_interview, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/edit_interview', 'edit_interview', edit_interview, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/invite', 'mark_invited', mark_invited)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/uninvite', 'unmark_invited', unmark_invited)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/offer_made', 'mark_offer', mark_offer)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/offer_not_made', 'unmark_offer', unmark_offer)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/hire', 'mark_hired', mark_hired)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/unhire', 'unmark_hired', unmark_hired)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/unreject', 'remove_reject_reason', remove_reject_reason)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/undecline', 'remove_decline_reason', remove_decline_reason)

app.add_url_rule('/stats', 'stats', stats, methods=['GET', 'POST'])
app.add_url_rule('/search', 'search', search, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
