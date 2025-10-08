# Third Party Stuff
from django.contrib import admin

# nexus Stuff
from nexus.proposals.models import Proposal, ProposalKind
from nexus.proposals.reviewer_models import ProposalReview, ProposalReviewer
from nexus.proposals.scoring_models import ProposalOverallScore, ProposalScore, ReviewCriteria


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Proposal info', {'fields': ('title', 'speaker', 'status', 'kind', 'level',
                                      'duration', 'abstract', 'description')}),
        ('Timing', {'fields': ('accepted_at',)}),
    )
    list_display = ('speaker', 'title', 'submitted_at', 'status')
    list_filter = ('speaker', 'submitted_at', 'status')
    ordering = ('submitted_at',)
    search_fields = ('speaker__email', 'speaker__first_name', 'speaker__last_name')


@admin.register(ProposalKind)
class ProposalKindAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Proposal details', {'fields': ('kind',)}),
    )
    list_display = ('kind',)


@admin.register(ProposalReviewer)
class ProposalReviewerAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'reviewer', 'assigned_at', 'assigned_by')
    list_filter = ('assigned_at', 'reviewer')
    search_fields = ('proposal__title', 'reviewer__email')
    readonly_fields = ('assigned_at',)


@admin.register(ProposalReview)
class ProposalReviewAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Review info', {'fields': ('proposal', 'reviewer', 'status', 'recommendation')}),
        ('Comments', {'fields': ('comments', 'feedback_for_speaker')}),
        ('Metadata', {'fields': ('reviewed_at', 'created_at', 'modified_at')}),
    )
    list_display = ('proposal', 'reviewer', 'recommendation', 'status', 'reviewed_at')
    list_filter = ('status', 'recommendation', 'reviewed_at')
    search_fields = ('proposal__title', 'reviewer__email', 'comments')
    readonly_fields = ('created_at', 'modified_at')


@admin.register(ReviewCriteria)
class ReviewCriteriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'max_score', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('weight', 'max_score', 'is_active', 'order')


@admin.register(ProposalScore)
class ProposalScoreAdmin(admin.ModelAdmin):
    list_display = ('review', 'criteria', 'score', 'weighted_score')
    list_filter = ('criteria', 'score')
    search_fields = ('review__proposal__title', 'review__reviewer__email')
    readonly_fields = ('created_at', 'modified_at')


@admin.register(ProposalOverallScore)
class ProposalOverallScoreAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'weighted_average', 'average_score', 'total_reviews', 'last_calculated_at')
    search_fields = ('proposal__title',)
    readonly_fields = ('average_score', 'weighted_average', 'total_reviews', 'last_calculated_at',
                      'created_at', 'modified_at')
    actions = ['recalculate_scores']

    def recalculate_scores(self, request, queryset):
        for overall_score in queryset:
            overall_score.recalculate_scores()
        self.message_user(request, f'{queryset.count()} scores recalculated successfully.')
    recalculate_scores.short_description = 'Recalculate selected scores'
