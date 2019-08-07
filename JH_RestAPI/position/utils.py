from position.models import JobPosition


def get_or_insert_position(title):
    jt = JobPosition.objects.all().get_or_create(job_title__iexact=title)
    jt.save()
    return jt