import re
from django.db.models import Q
from django.utils import timezone

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


def calculate_job_match(student, job):
    """
    Calculate an explainable match score (0 to 100%) between a Student profile and a Job.
    Returns dict with match_score, matched_skills, missing_skills, dept_eligible, cgpa_eligible, explanations.
    """
    explanations = []
    total_score = 0.0

    # 1. Skills Matching (Weight: 50 points)
    student_skills_list = [s.strip().lower() for s in student.get_skills_list()]
    req_skills_list = job.get_required_skills_list()
    pref_skills_list = job.get_preferred_skills_list()

    matched_skills = []
    missing_skills = []

    if req_skills_list:
        matched_req_count = 0
        for req_skill in req_skills_list:
            req_clean = req_skill.strip().lower()
            # Direct match or substring match
            is_matched = any(
                req_clean == s or req_clean in s or s in req_clean
                for s in student_skills_list
            )
            if not is_matched and student.experience:
                is_matched = req_clean in student.experience.lower()
            if not is_matched and student.projects:
                is_matched = req_clean in student.projects.lower()

            if is_matched:
                matched_req_count += 1
                matched_skills.append(req_skill)
                explanations.append(f"✓ {req_skill} (Required skill matched)")
            else:
                missing_skills.append(req_skill)
                explanations.append(f"△ {req_skill} (Not listed in profile)")

        req_score = (matched_req_count / len(req_skills_list)) * 40.0
        total_score += req_score
    else:
        total_score += 40.0  # Full points if no specific required skills listed

    # Preferred Skills Bonus (Up to 10 points)
    if pref_skills_list:
        matched_pref_count = 0
        for pref_skill in pref_skills_list:
            pref_clean = pref_skill.strip().lower()
            if any(pref_clean == s or pref_clean in s for s in student_skills_list):
                matched_pref_count += 1
                explanations.append(f"✓ {pref_skill} (Preferred skill bonus)")
        pref_score = (matched_pref_count / len(pref_skills_list)) * 10.0
        total_score += pref_score
    else:
        total_score += 10.0

    # 2. Department Eligibility (Weight: 20 points)
    eligible_depts = job.get_eligible_departments_list()
    dept_eligible = True
    if eligible_depts:
        if student.department:
            dept_clean = student.department.strip().lower()
            dept_eligible = any(
                dept_clean in ed.lower() or ed.lower() in dept_clean or ed.lower() == 'all'
                for ed in eligible_depts
            )
            if dept_eligible:
                total_score += 20.0
                explanations.append(f"✓ Eligible Department ({student.department})")
            else:
                explanations.append(f"✕ Department ({student.department}) not listed in eligible departments")
        else:
            # If student hasn't set department yet, give partial credit
            total_score += 10.0
            dept_eligible = False
    else:
        total_score += 20.0
        explanations.append("✓ Open to all departments")

    # 3. CGPA Eligibility (Weight: 15 points)
    cgpa_eligible = True
    if job.minimum_cgpa:
        if student.cgpa:
            if student.cgpa >= job.minimum_cgpa:
                total_score += 15.0
                explanations.append(f"✓ CGPA {student.cgpa} meets minimum requirement ({job.minimum_cgpa})")
            else:
                cgpa_eligible = False
                explanations.append(f"✕ CGPA {student.cgpa} below minimum requirement ({job.minimum_cgpa})")
        else:
            total_score += 7.5
            cgpa_eligible = False
            explanations.append(f"△ CGPA not specified (Minimum {job.minimum_cgpa} required)")
    else:
        total_score += 15.0
        explanations.append("✓ No minimum CGPA criteria")

    # 4. Project & Experience Relevance (Weight: 15 points)
    exp_score = 0.0
    text_to_check = f"{student.experience or ''} {student.projects or ''} {student.bio or ''}".lower()
    if text_to_check.strip() and job.description:
        job_desc = job.description.lower()
        if nlp:
            try:
                doc_student = nlp(text_to_check[:1000])
                keywords_student = set(
                    t.lemma_ for t in doc_student if not t.is_stop and not t.is_punct and len(t.text) > 2
                )
                matched_kw = [kw for kw in keywords_student if kw in job_desc]
                if keywords_student:
                    rel_ratio = len(matched_kw) / min(len(keywords_student), 20)
                    exp_score = min(15.0, rel_ratio * 15.0)
            except Exception:
                exp_score = 7.5
        else:
            exp_score = 7.5
    else:
        exp_score = 5.0

    total_score += exp_score

    match_percentage = min(99, max(30, int(round(total_score))))

    return {
        'match_score': match_percentage,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'dept_eligible': dept_eligible,
        'cgpa_eligible': cgpa_eligible,
        'explanations': explanations,
    }


def get_recommended_jobs_for_student(student, active_jobs=None, limit=10):
    """
    Generates personalized job recommendations for a student ordered by match score.
    Returns list of dicts: {'job': job_obj, 'match_info': match_dict}
    """
    from core.models import Job

    if active_jobs is None:
        now = timezone.now()
        active_jobs = Job.objects.filter(
            status='active',
            company__verification_status='approved',
            deadline__gt=now
        ).select_related('company')

    recommendations = []
    for job in active_jobs:
        match_info = calculate_job_match(student, job)
        recommendations.append({
            'job': job,
            'match_info': match_info,
            'match_score': match_info['match_score']
        })

    # Sort descending by match score
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    return recommendations[:limit]
