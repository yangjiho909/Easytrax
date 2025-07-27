#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 액션 플랜 생성기 (Action Plan Generator)
- 규제 위반 시 구체적인 해결 방안 제시
- 통관 거부 사례 분석 후 단계별 대응 전략 제공
- 사용자의 "그래서 뭘 어떻게 해야 하나요?" 질문에 답변
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class ActionStep:
    """액션 스텝 정보"""
    step_number: int
    title: str
    description: str
    priority: str  # "긴급", "높음", "보통", "낮음"
    estimated_time: str
    responsible_party: str
    cost_estimate: str
    required_documents: List[str]
    notes: str

@dataclass
class ActionPlan:
    """액션 플랜 정보"""
    plan_id: str
    issue_type: str  # "규제위반", "통관거부", "서류불완전" 등
    country: str
    product: str
    severity: str  # "심각", "보통", "경미"
    total_estimated_cost: str
    total_estimated_time: str
    steps: List[ActionStep]
    risk_level: str
    success_probability: str
    created_at: datetime

class ActionPlanGenerator:
    """액션 플랜 생성기"""
    
    def __init__(self):
        self.regulatory_actions = {
            "중국": {
                "라면": {
                    "라벨링_위반": {
                        "긴급도": "높음",
                        "예상_처리기간": "2-4주",
                        "예상_비용": "500-1,000만원",
                        "단계별_액션": [
                            {
                                "step": 1,
                                "title": "즉시 제품 생산 중단",
                                "description": "위반된 라벨이 적용된 제품의 생산을 즉시 중단하고, 유통 중인 제품 회수 준비",
                                "priority": "긴급",
                                "time": "즉시",
                                "responsible": "생산팀장",
                                "cost": "생산 중단 손실",
                                "documents": ["생산 중단 보고서", "재고 현황"],
                                "notes": "법적 책임 회피를 위해 즉시 조치 필요"
                            },
                            {
                                "step": 2,
                                "title": "중국 현지 법무팀 구성",
                                "description": "중국 현지 법무 전문가와 한국 본사 법무팀으로 구성된 대응팀 구성",
                                "priority": "긴급",
                                "time": "24시간 이내",
                                "responsible": "법무팀장",
                                "cost": "법무 자문비 200-300만원",
                                "documents": ["법무팀 구성 보고서", "전문가 계약서"],
                                "notes": "현지 법규에 정통한 전문가 필수"
                            },
                            {
                                "step": 3,
                                "title": "위반 사항 상세 분석",
                                "description": "GB 7718-2025 규정과 현재 라벨을 대조하여 구체적 위반 사항 파악",
                                "priority": "높음",
                                "time": "3-5일",
                                "responsible": "품질관리팀",
                                "cost": "분석 비용 50만원",
                                "documents": ["규정 대조 분석서", "위반 사항 리스트"],
                                "notes": "중국어 전문가 참여 필요"
                            },
                            {
                                "step": 4,
                                "title": "새로운 라벨 디자인 및 제작",
                                "description": "규정에 맞는 새로운 라벨 디자인 제작 및 인쇄",
                                "priority": "높음",
                                "time": "1-2주",
                                "responsible": "디자인팀 + 생산팀",
                                "cost": "디자인비 100만원 + 인쇄비 200만원",
                                "documents": ["새 라벨 디자인", "인쇄 견적서"],
                                "notes": "중국어 표기 정확성 재검토 필수"
                            },
                            {
                                "step": 5,
                                "title": "중국 현지 기관과 협의",
                                "description": "NMPA(국가약품감독관리국)와 협의하여 라벨 변경 승인 요청",
                                "priority": "높음",
                                "time": "1-2주",
                                "responsible": "해외사업팀",
                                "cost": "행정비용 100만원",
                                "documents": ["라벨 변경 신청서", "새 라벨 샘플"],
                                "notes": "현지 대리인을 통한 접촉 권장"
                            },
                            {
                                "step": 6,
                                "title": "기존 제품 라벨 교체",
                                "description": "유통 중인 제품의 라벨을 새로운 라벨로 교체",
                                "priority": "보통",
                                "time": "2-3주",
                                "responsible": "물류팀",
                                "cost": "라벨 교체 비용 300만원",
                                "documents": ["라벨 교체 계획서", "진행 상황 보고서"],
                                "notes": "소비자 혼란 방지를 위한 단계적 교체"
                            }
                        ]
                    },
                    "위생증명서_불완전": {
                        "긴급도": "높음",
                        "예상_처리기간": "3-6주",
                        "예상_비용": "300-500만원",
                        "단계별_액션": [
                            {
                                "step": 1,
                                "title": "필요 서류 목록 확인",
                                "description": "중국 수입 요구 서류 목록과 현재 보유 서류 대조",
                                "priority": "높음",
                                "time": "1-2일",
                                "responsible": "해외사업팀",
                                "cost": "분석 비용 20만원",
                                "documents": ["서류 체크리스트", "현재 보유 서류 목록"],
                                "notes": "중국 현지 요구사항 정확 파악 필요"
                            },
                            {
                                "step": 2,
                                "title": "부족한 서류 발급 신청",
                                "description": "한국 식약처, 상공회의소 등에서 필요한 증명서 발급",
                                "priority": "높음",
                                "time": "2-3주",
                                "responsible": "행정팀",
                                "cost": "발급 수수료 50만원",
                                "documents": ["증명서 발급 신청서", "수수료 납부증"],
                                "notes": "공증 및 아포스티유 확인 필요"
                            },
                            {
                                "step": 3,
                                "title": "중국어 번역 및 공증",
                                "description": "발급받은 서류를 중국어로 번역하고 공증",
                                "priority": "높음",
                                "time": "1주",
                                "responsible": "번역팀",
                                "cost": "번역비 100만원 + 공증비 50만원",
                                "documents": ["번역문", "공증서"],
                                "notes": "공인번역사 번역 필수"
                            },
                            {
                                "step": 4,
                                "title": "중국 현지 검증",
                                "description": "중국 현지에서 서류 유효성 검증",
                                "priority": "높음",
                                "time": "1주",
                                "responsible": "해외사업팀",
                                "cost": "검증 비용 30만원",
                                "documents": ["검증 결과서"],
                                "notes": "현지 대리인을 통한 검증 권장"
                            }
                        ]
                    }
                }
            },
            "미국": {
                "라면": {
                    "FDA_등록_미완료": {
                        "긴급도": "높음",
                        "예상_처리기간": "4-8주",
                        "예상_비용": "1,000-2,000만원",
                        "단계별_액션": [
                            {
                                "step": 1,
                                "title": "FDA FFR 등록 신청",
                                "description": "FDA Food Facility Registration (FFR) 온라인 등록",
                                "priority": "긴급",
                                "time": "1-2주",
                                "responsible": "해외사업팀",
                                "cost": "등록비 5,000달러",
                                "documents": ["FFR 등록 신청서", "회사 정보", "제품 정보"],
                                "notes": "2년마다 갱신 필요, 미국 현지 에이전트 지정 필수"
                            },
                            {
                                "step": 2,
                                "title": "FSVP 프로그램 준비",
                                "description": "Foreign Supplier Verification Program 준비 및 구현",
                                "priority": "높음",
                                "time": "2-3주",
                                "responsible": "품질관리팀",
                                "cost": "시스템 구축비 500만원",
                                "documents": ["FSVP 계획서", "검증 절차서"],
                                "notes": "FDA 규정에 맞는 검증 시스템 구축"
                            },
                            {
                                "step": 3,
                                "title": "제품 라벨 FDA 규정 준수 확인",
                                "description": "2025년 FDA 라벨링 규정에 맞는 라벨 검토 및 수정",
                                "priority": "높음",
                                "time": "1-2주",
                                "responsible": "품질관리팀",
                                "cost": "라벨 수정비 200만원",
                                "documents": ["라벨 검토 보고서", "수정된 라벨"],
                                "notes": "알레르기 성분 표기 및 영양성분표 확인"
                            },
                            {
                                "step": 4,
                                "title": "미국 현지 대리인 선정",
                                "description": "FDA와의 소통을 위한 미국 현지 대리인 선정",
                                "priority": "높음",
                                "time": "1주",
                                "responsible": "해외사업팀",
                                "cost": "대리인 계약비 300만원",
                                "documents": ["대리인 계약서", "대리인 정보"],
                                "notes": "FDA 규정에 정통한 전문 대리인 선정"
                            }
                        ]
                    },
                    "알레르기_표기_위반": {
                        "긴급도": "높음",
                        "예상_처리기간": "2-4주",
                        "예상_비용": "400-800만원",
                        "단계별_액션": [
                            {
                                "step": 1,
                                "title": "즉시 제품 회수",
                                "description": "알레르기 표기가 잘못된 제품 즉시 회수",
                                "priority": "긴급",
                                "time": "즉시",
                                "responsible": "물류팀",
                                "cost": "회수 비용 200만원",
                                "documents": ["제품 회수 계획서", "회수 현황"],
                                "notes": "소비자 안전을 위한 즉시 조치"
                            },
                            {
                                "step": 2,
                                "title": "알레르기 성분 재분석",
                                "description": "제품의 알레르기 성분을 정확히 분석",
                                "priority": "높음",
                                "time": "1주",
                                "responsible": "품질관리팀",
                                "cost": "분석 비용 100만원",
                                "documents": ["알레르기 성분 분석서"],
                                "notes": "FDA 9대 알레르기 성분 기준 적용"
                            },
                            {
                                "step": 3,
                                "title": "라벨 수정 및 재인쇄",
                                "description": "정확한 알레르기 정보로 라벨 수정",
                                "priority": "높음",
                                "time": "1-2주",
                                "responsible": "디자인팀",
                                "cost": "라벨 수정비 200만원",
                                "documents": ["수정된 라벨", "인쇄 견적서"],
                                "notes": "알레르기 성분 강조 표기 필수"
                            },
                            {
                                "step": 4,
                                "title": "FDA에 수정 사항 보고",
                                "description": "라벨 수정 사항을 FDA에 보고",
                                "priority": "높음",
                                "time": "1주",
                                "responsible": "해외사업팀",
                                "cost": "보고 비용 50만원",
                                "documents": ["라벨 수정 보고서"],
                                "notes": "FDA 규정 준수 확인"
                            }
                        ]
                    }
                }
            }
        }
        
        self.customs_rejection_actions = {
            "서류_불완전": {
                "긴급도": "높음",
                "예상_처리기간": "1-2주",
                "예상_비용": "100-300만원",
                "단계별_액션": [
                    {
                        "step": 1,
                        "title": "거부 사유 상세 확인",
                        "description": "세관에서 제시한 거부 사유를 정확히 파악",
                        "priority": "긴급",
                        "time": "1일",
                        "responsible": "해외사업팀",
                        "cost": "분석 비용 20만원",
                        "documents": ["거부 사유서", "필요 서류 목록"],
                        "notes": "세관 담당자와 직접 소통 권장"
                    },
                    {
                        "step": 2,
                        "title": "부족한 서류 즉시 준비",
                        "description": "거부 사유에 따른 부족한 서류를 즉시 준비",
                        "priority": "높음",
                        "time": "3-5일",
                        "responsible": "행정팀",
                        "cost": "서류 발급비 50만원",
                        "documents": ["필요 서류 목록", "발급 진행상황"],
                        "notes": "공증 및 번역 필요 여부 확인"
                    },
                    {
                        "step": 3,
                        "title": "재신고 준비",
                        "description": "완전한 서류로 재신고 준비",
                        "priority": "높음",
                        "time": "1-2일",
                        "responsible": "해외사업팀",
                        "cost": "재신고 수수료 30만원",
                        "documents": ["재신고 서류", "추가 서류"],
                        "notes": "이전 거부 사유가 해결되었는지 재확인"
                    }
                ]
            },
            "품질_검사_불합격": {
                "긴급도": "높음",
                "예상_처리기간": "2-4주",
                "예상_비용": "500-1,000만원",
                "단계별_액션": [
                    {
                        "step": 1,
                        "title": "검사 결과 상세 분석",
                        "description": "품질 검사 불합격 사유를 정확히 파악",
                        "priority": "긴급",
                        "time": "1-2일",
                        "responsible": "품질관리팀",
                        "cost": "분석 비용 50만원",
                        "documents": ["검사 결과서", "불합격 사유 분석서"],
                        "notes": "검사기관과 직접 소통하여 정확한 사유 파악"
                    },
                    {
                        "step": 2,
                        "title": "제품 품질 개선",
                        "description": "불합격 사유에 따른 제품 품질 개선",
                        "priority": "높음",
                        "time": "1-2주",
                        "responsible": "생산팀",
                        "cost": "품질 개선비 300만원",
                        "documents": ["품질 개선 계획서", "개선 결과 보고서"],
                        "notes": "해당 국가의 품질 기준에 맞춘 개선"
                    },
                    {
                        "step": 3,
                        "title": "재검사 신청",
                        "description": "개선된 제품으로 재검사 신청",
                        "priority": "높음",
                        "time": "1주",
                        "responsible": "해외사업팀",
                        "cost": "재검사비 150만원",
                        "documents": ["재검사 신청서", "개선 증명서"],
                        "notes": "이전 불합격 사유가 해결되었음을 명시"
                    }
                ]
            }
        }

    def generate_regulatory_action_plan(self, country: str, product: str, issue: str) -> ActionPlan:
        """규제 위반에 대한 액션 플랜 생성"""
        
        if country not in self.regulatory_actions:
            return self._generate_default_plan("규제위반", country, product)
            
        if product not in self.regulatory_actions[country]:
            return self._generate_default_plan("규제위반", country, product)
            
        if issue not in self.regulatory_actions[country][product]:
            return self._generate_default_plan("규제위반", country, product)
        
        action_data = self.regulatory_actions[country][product][issue]
        
        steps = []
        for step_data in action_data["단계별_액션"]:
            step = ActionStep(
                step_number=step_data["step"],
                title=step_data["title"],
                description=step_data["description"],
                priority=step_data["priority"],
                estimated_time=step_data["time"],
                responsible_party=step_data["responsible"],
                cost_estimate=step_data["cost"],
                required_documents=step_data["documents"],
                notes=step_data["notes"]
            )
            steps.append(step)
        
        plan = ActionPlan(
            plan_id=f"REG_{country}_{product}_{issue}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            issue_type="규제위반",
            country=country,
            product=product,
            severity=action_data["긴급도"],
            total_estimated_cost=action_data["예상_비용"],
            total_estimated_time=action_data["예상_처리기간"],
            steps=steps,
            risk_level="높음" if action_data["긴급도"] in ["긴급", "높음"] else "보통",
            success_probability="80%" if action_data["긴급도"] == "높음" else "90%",
            created_at=datetime.now()
        )
        
        return plan

    def generate_customs_rejection_action_plan(self, rejection_type: str) -> ActionPlan:
        """통관 거부에 대한 액션 플랜 생성"""
        
        if rejection_type not in self.customs_rejection_actions:
            return self._generate_default_plan("통관거부", "미확정", "미확정")
        
        action_data = self.customs_rejection_actions[rejection_type]
        
        steps = []
        for step_data in action_data["단계별_액션"]:
            step = ActionStep(
                step_number=step_data["step"],
                title=step_data["title"],
                description=step_data["description"],
                priority=step_data["priority"],
                estimated_time=step_data["time"],
                responsible_party=step_data["responsible"],
                cost_estimate=step_data["cost"],
                required_documents=step_data["documents"],
                notes=step_data["notes"]
            )
            steps.append(step)
        
        plan = ActionPlan(
            plan_id=f"CUSTOMS_{rejection_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            issue_type="통관거부",
            country="미확정",
            product="미확정",
            severity=action_data["긴급도"],
            total_estimated_cost=action_data["예상_비용"],
            total_estimated_time=action_data["예상_처리기간"],
            steps=steps,
            risk_level="높음" if action_data["긴급도"] in ["긴급", "높음"] else "보통",
            success_probability="85%",
            created_at=datetime.now()
        )
        
        return plan

    def _generate_default_plan(self, issue_type: str, country: str, product: str) -> ActionPlan:
        """기본 액션 플랜 생성"""
        steps = [
            ActionStep(
                step_number=1,
                title="문제 상황 상세 분석",
                description="발생한 문제의 원인과 영향을 정확히 파악",
                priority="긴급",
                estimated_time="1-2일",
                responsible_party="품질관리팀",
                cost_estimate="분석 비용 50만원",
                required_documents=["문제 분석 보고서"],
                notes="전문가 자문 필요"
            ),
            ActionStep(
                step_number=2,
                title="해결 방안 수립",
                description="문제 해결을 위한 구체적인 방안 수립",
                priority="높음",
                estimated_time="2-3일",
                responsible_party="관리팀",
                cost_estimate="계획 수립 비용 30만원",
                required_documents=["해결 방안 계획서"],
                notes="여러 대안 검토"
            ),
            ActionStep(
                step_number=3,
                title="실행 및 모니터링",
                description="수립된 방안을 실행하고 결과 모니터링",
                priority="높음",
                estimated_time="1-2주",
                responsible_party="실행팀",
                cost_estimate="실행 비용 200만원",
                required_documents=["실행 계획서", "진행 상황 보고서"],
                notes="정기적인 진행 상황 점검"
            )
        ]
        
        return ActionPlan(
            plan_id=f"DEFAULT_{issue_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            issue_type=issue_type,
            country=country,
            product=product,
            severity="보통",
            total_estimated_cost="300만원",
            total_estimated_time="2-3주",
            steps=steps,
            risk_level="보통",
            success_probability="70%",
            created_at=datetime.now()
        )

    def format_action_plan(self, plan: ActionPlan) -> str:
        """액션 플랜을 사용자 친화적인 형태로 포맷팅"""
        
        output = []
        output.append("🎯 **액션 플랜 생성 완료**")
        output.append("=" * 60)
        output.append(f"📋 **플랜 ID**: {plan.plan_id}")
        output.append(f"🌍 **국가**: {plan.country}")
        output.append(f"📦 **제품**: {plan.product}")
        output.append(f"⚠️ **문제 유형**: {plan.issue_type}")
        output.append(f"🚨 **심각도**: {plan.severity}")
        output.append(f"💰 **예상 총 비용**: {plan.total_estimated_cost}")
        output.append(f"⏰ **예상 소요 기간**: {plan.total_estimated_time}")
        output.append(f"🎯 **성공 확률**: {plan.success_probability}")
        output.append(f"📅 **생성일**: {plan.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        output.append("\n📋 **단계별 실행 계획**")
        output.append("-" * 40)
        
        for step in plan.steps:
            priority_icon = {
                "긴급": "🚨",
                "높음": "⚠️", 
                "보통": "📋",
                "낮음": "📝"
            }.get(step.priority, "📋")
            
            output.append(f"\n{priority_icon} **Step {step.step_number}: {step.title}**")
            output.append(f"   📝 **설명**: {step.description}")
            output.append(f"   ⏰ **소요시간**: {step.estimated_time}")
            output.append(f"   👤 **담당자**: {step.responsible_party}")
            output.append(f"   💰 **예상비용**: {step.cost_estimate}")
            output.append(f"   📄 **필요서류**: {', '.join(step.required_documents)}")
            output.append(f"   💡 **참고사항**: {step.notes}")
        
        output.append("\n🎯 **핵심 성공 요인**")
        output.append("-" * 20)
        output.append("1. **즉시 대응**: 문제 발생 시 24시간 이내 초기 대응")
        output.append("2. **전문가 활용**: 현지 법무/통관 전문가 자문")
        output.append("3. **체계적 관리**: 단계별 진행 상황 추적")
        output.append("4. **문서화**: 모든 과정의 문서화 및 증빙")
        output.append("5. **소통 강화**: 관련 기관과의 지속적 소통")
        
        output.append("\n⚠️ **주의사항**")
        output.append("-" * 15)
        output.append("• 각 단계 완료 후 다음 단계 진행 전 검토 필수")
        output.append("• 예상보다 시간/비용이 더 소요될 수 있음")
        output.append("• 현지 법규 변경 가능성 고려")
        output.append("• 정기적인 진행 상황 보고 체계 구축")
        
        return "\n".join(output)

def main():
    """테스트 함수"""
    generator = ActionPlanGenerator()
    
    # 테스트 케이스들
    test_cases = [
        ("중국", "라면", "라벨링_위반"),
        ("미국", "라면", "FDA_등록_미완료"),
        ("통관거부", "서류_불완전"),
    ]
    
    print("🎯 액션 플랜 생성기 테스트")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 테스트 케이스 {i}: {test_case}")
        
        if len(test_case) == 3:
            country, product, issue = test_case
            plan = generator.generate_regulatory_action_plan(country, product, issue)
        else:
            rejection_type = test_case[0]
            plan = generator.generate_customs_rejection_action_plan(rejection_type)
        
        formatted_plan = generator.format_action_plan(plan)
        print(formatted_plan)
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 