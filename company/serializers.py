from django.db.models import Count
from rest_framework import serializers

from review.models import Review, CompanyEmploymentAuth
from .models import Company


class CompanyBasicsSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Company.objects.create(**validated_data)

    class Meta:
        model = Company
        fields = ('id', 'company', 'logo', 'location_lat', 'location_lon', 'location_address')


class CompanySerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    supported_employment_auths = serializers.SerializerMethodField()
    review_id = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    def get_review_count(self, obj):
        if 'position' in self.context:
            position = self.context.get('position')
            review = Review.objects.filter(
                is_published=True, company__pk=obj.pk, position=position)
            return review.count()
        else:
            return Review.objects.filter(is_published=True, company__pk=obj.pk).count()

    def get_review_id(self, obj):
        if 'position' in self.context:
            position = self.context.get('position')
            review = Review.objects.filter(user=self.context.get(
                'user'), company__pk=obj.pk, position=position)
            if review.count() == 0:
                return None
            return review[0].pk
        else:
            return None

    def get_ratings(self, obj):
        ratings = []
        for i in range(1, 6):
            rating = {'id': i, 'count': Review.objects.filter(company=obj, overall_company_experience=i,
                                                              is_published=True).aggregate(
                Count('overall_company_experience'))['overall_company_experience__count']}
            ratings.append(rating)
        return ratings

    def get_supported_employment_auths(self, obj):
        from review.models import EmploymentAuth
        from review.serializers import EmploymentAuthSerializer
        auths = []
        for auth in EmploymentAuth.objects.all():
            a_ser = EmploymentAuthSerializer(instance=auth, many=False).data
            emp_auths = CompanyEmploymentAuth.objects.filter(
                review__company=obj, employment_auth=auth)
            a_ser['yes'] = emp_auths.filter(value=True).aggregate(
                Count('value'))['value__count']
            a_ser['no'] = emp_auths.filter(value=False).aggregate(
                Count('value'))['value__count']
            auths.append(a_ser)
        return auths

    def create(self, validated_data):
        return Company.objects.create(**validated_data)

    class Meta:
        model = Company
        fields = ('__all__')
