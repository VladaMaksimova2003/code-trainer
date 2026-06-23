"""POST /tasks/analyze-code — teacher insights (core + analytics, analytics ≠ grading)."""

from fastapi import APIRouter, HTTPException, Depends



from application.auth.dto import CurrentUserResult

from application.tasks.services.code_analysis_service import CodeAnalysisService

from api.tasks.schemas.requests import AnalyzeCodeRequest

from api.tasks.schemas.responses import AnalyzeCodeResponse, DetectedPatternResponse

from api.dependencies.authorization import require_permission

from domain.policies.permissions.permissions import Permission

from application.analysis.concept_analysis_service import ConceptAnalysisService



router = APIRouter()





def _code_analysis_service() -> CodeAnalysisService:

    return CodeAnalysisService(ConceptAnalysisService())





@router.post("/analyze-code", response_model=AnalyzeCodeResponse)

async def analyze_code(

    request: AnalyzeCodeRequest,

    current_user: CurrentUserResult = Depends(

        require_permission(Permission.CREATE_ASSIGNMENTS)

    ),

):

    try:

        result = _code_analysis_service().analyze(request.code, request.language)

    except Exception as exc:

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AnalyzeCodeResponse(

        patterns=[

            DetectedPatternResponse(

                id=p.id,

                type=p.type,

                label=p.label,

                confidence=1.0,

                source_construct=p.source_construct,

            )

            for p in result.patterns

        ],

        raw_constructs=list(result.raw_constructs),

        semantic_ir={

            **result.exam,

            "analytics": result.analytics,

        },

    )

