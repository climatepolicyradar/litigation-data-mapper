from enum import Enum


class EventType(Enum):
    ADMINISTRATIVE_ORDER = "Administrative Order"
    AFFIDAVIT = "Affidavit"
    AFFIRMATION = "Affirmation"
    AFFIXED = "Affixed"
    AMICUS_BRIEF = "Amicus Brief"
    AMICUS_MOTION = "Amicus Motion"
    ANSWER = "Answer"
    APPEAL = "Appeal"
    APPENDIX = "Appendix"
    APPLICATION = "Application"
    APPLICATION_FOR_ADMINISTRATIVE_STAY = "Application For Administrative Stay"
    ASSURANCE_OF_DISCONTINUANCE = "Assurance Of Discontinuance"
    BILL_OF_COMPLAINT = "Bill Of Complaint"
    BRIEF = "Brief"
    COMPLAINT = "Complaint"
    CONCILIATION_AGREEMENT = "Conciliation Agreement"
    CONSENT_DECREE = "Consent Decree"
    CONSENT_MOTION = "Consent Motion"
    CONSENT_ORDER = "Consent Order"
    DECLARATION = "Declaration"
    DECISION = "Decision"
    EXHIBIT = "Exhibit"
    EXPERT_REPORT = "Expert Report"
    FEDERAL_REGISTER_NOTICE = "Federal Register Notice"
    FILING_YEAR_FOR_ACTION = "Filing Year For Action"
    FINAL_DECISION = "Final Decision"
    FINAL_DETERMINATION = "Final Determination"
    FINDINGS_AND_RECOMMENDATIONS = "Findings And Recommendations"
    FINDINGS_OF_FACT_AND_CONCLUSIONS_OF_LAW = "Findings Of Fact And Conclusions Of Law"
    JOINT_PROPOSED_REMEDY = "Joint Proposed Remedy"
    JOINDER = "Joinder"
    JUDGMENT = "Judgment"
    LETTER = "Letter"
    MEMORANDUM = "Memorandum"
    MEMORANDUM_AND_ORDER = "Memorandum And Order"
    MEMORANDUM_DECISION = "Memorandum Decision"
    MEMORANDUM_OF_DECISION = "Memorandum Of Decision"
    MEMORANDUM_OF_LAW = "Memorandum Of Law"
    MEMORANDUM_OPINION = "Memorandum Opinion"
    MEMORANDUM_OPINION_AND_ORDER = "Memorandum Opinion And Order"
    MINUTE_ORDER = "Minute Order"
    MINUTE_PROCEEDINGS = "Minute Proceedings"
    MOTION = "Motion"
    MOTION_FOR_SUMMARY_JUDGMENT = "Motion For Summary Judgment"
    MOTION_TO_DISMISS = "Motion To Dismiss"
    MOTION_TO_INTERVENE = "Motion To Intervene"
    NOTICE = "Notice"
    NOTICE_OF_APPEAL = "Notice Of Appeal"
    NOTICE_OF_INTENT = "Notice Of Intent"
    NOTICE_OF_INTENT_TO_SUE = "Notice Of Intent To Sue"
    NOTICE_OF_REMOVAL = "Notice Of Removal"
    NOTICE_OF_RULING = "Notice Of Ruling"
    NOTICE_OF_VOLUNTARY_DISMISSAL = "Notice Of Voluntary Dismissal"
    NOTIFICATION = "Notification"
    OBJECTION = "Objection"
    OPINION = "Opinion"
    OPINION_AND_ORDER = "Opinion And Order"
    OPPOSITION = "Opposition"
    ORDER = "Order"
    ORDER_DENYING_PETITION_FOR_REVIEW = "Order Denying Petition For Review"
    ORDER_LIST = "Order List"
    ORDER_TO_SHOW_CAUSE = "Order To Show Cause"
    PETITION = "Petition"
    PETITION_FOR_RECONSIDERATION = "Petition For Reconsideration"
    PETITION_FOR_REHEARING = "Petition For Rehearing"
    PETITION_FOR_REVIEW = "Petition For Review"
    PETITION_FOR_RULEMAKING = "Petition For Rulemaking"
    PETITION_FOR_WRIT_OF_CERTIORARI = "Petition For Writ Of Certiorari"
    PETITION_FOR_WRIT_OF_MANDATE = "Petition For Writ Of Mandate"
    PLEA = "Plea"
    POINTS_OF_CLAIM = "Points Of Claim"
    PRESS_RELEASE = "Press Release"
    REPLY = "Reply"
    REQUEST = "Request"
    REQUEST_FOR_ADMINISTRATIVE_STAY = "Request For Administrative Stay"
    REQUEST_FOR_REHEARING = "Request For Rehearing"
    REPORT_AND_RECOMMENDATION = "Report And Recommendation"
    RESPONSE = "Response"
    RESPONSE_TO_PETITION_FOR_RULEMAKING = "Response To Petition For Rulemaking"
    RULING = "Ruling"
    SETTLEMENT_AGREEMENT = "Settlement Agreement"
    STATEMENT = "Statement"
    STATEMENT_OF_ISSUES = "Statement Of Issues"
    STATEMENT_OF_REPLY = "Statement Of Reply"
    STATUS_REPORT = "Status Report"
    STIPULATION = "Stipulation"
    SUBPOENA = "Subpoena"
    SUR_REPLY = "Sur-Reply"
    SUMMONS = "Summons"
    SUPPLEMENT = "Supplement"
    TENTATIVE_RULING = "Tentative Ruling"
    TRANSCRIPT = "Transcript"
    VERDICT = "Verdict"
    SUBSTITUTION_OF_PARTIES = "Substitution Of Parties"


class ConsolidatedEventType(Enum):
    """Consolidated event types for mapping"""

    ORDER = "Order"
    AFFIDAVIT_DECLARATION = "Affidavit/Declaration"
    AMICUS_MOTION_BRIEF = "Amicus Motion/Brief"
    ANSWER = "Answer"
    APPEAL = "Appeal"
    APPENDIX_EXHIBIT_SUPPLEMENT = "Appendix/Exhibit/Supplement"
    APPLICATION = "Application"
    BRIEF = "Brief"
    COMPLAINT = "Complaint"
    CONSENT_DECREE_ORDER = "Consent Decree/Order"
    DECISION = "Decision"
    EXPERT_REPORT = "Expert Report"
    LETTER = "Letter"
    OBJECTIONS = "Objections"
    OPPOSITION = "Opposition"
    PETITION = "Petition"
    PETITION_FOR_REHEARING = "Petition for Rehearing"
    MOTION = "Motion"
    MOTION_FOR_SUMMARY_JUDGMENT = "Motion for Summary Judgment"
    MOTION_TO_DISMISS = "Motion to Dismiss"
    MOTION_TO_INTERVENE = "Motion to Intervene"
    NOTICE = "Notice"
    NOTICE_OF_INTENT_TO_SUE = "Notice of Intent to Sue"
    NOTICE_OF_REMOVAL = "Notice of Removal"
    NOTICE_OF_VOLUNTARY_DISMISSAL = "Notice of Voluntary Dismissal"
    PETITION_FOR_WRIT_OF_CERTIORARI = "Petition for Writ of Certiorari"
    PLEA = "Plea"
    PRESS_RELEASE = "Press Release"
    REPLY = "Reply"
    REQUEST = "Request"
    REPORT_AND_RECOMMENDATION = "Report and Recommendation"
    RESPONSE = "Response"
    SETTLEMENT_AGREEMENT = "Settlement Agreement"
    SETTLEMENT = "Settlement"
    STATEMENT = "Statement"
    STATUS_REPORT = "Status Report"
    STIPULATION = "Stipulation"
    SUBPOENA = "Subpoena"
    SUBSTITUTION_OF_PARTIES = "Substitution of Parties"
    TRANSCRIPT = "Transcript"
    VERDICT = "Verdict"


# Mapping from original EventType to ConsolidatedEventType based on Sabin's mapping
EVENT_TYPE_MAPPING = {
    EventType.ADMINISTRATIVE_ORDER: ConsolidatedEventType.ORDER,
    EventType.AFFIDAVIT: ConsolidatedEventType.AFFIDAVIT_DECLARATION,
    EventType.AFFIRMATION: ConsolidatedEventType.AFFIDAVIT_DECLARATION,
    EventType.AMICUS_BRIEF: ConsolidatedEventType.AMICUS_MOTION_BRIEF,
    EventType.AMICUS_MOTION: ConsolidatedEventType.AMICUS_MOTION_BRIEF,
    EventType.ANSWER: ConsolidatedEventType.ANSWER,
    EventType.APPEAL: ConsolidatedEventType.APPEAL,
    EventType.APPENDIX: ConsolidatedEventType.APPENDIX_EXHIBIT_SUPPLEMENT,
    EventType.APPLICATION: ConsolidatedEventType.APPLICATION,
    EventType.APPLICATION_FOR_ADMINISTRATIVE_STAY: ConsolidatedEventType.APPLICATION,
    EventType.BILL_OF_COMPLAINT: ConsolidatedEventType.MOTION,
    EventType.BRIEF: ConsolidatedEventType.BRIEF,
    EventType.COMPLAINT: ConsolidatedEventType.COMPLAINT,
    EventType.CONCILIATION_AGREEMENT: ConsolidatedEventType.SETTLEMENT_AGREEMENT,
    EventType.CONSENT_DECREE: ConsolidatedEventType.CONSENT_DECREE_ORDER,
    EventType.CONSENT_MOTION: ConsolidatedEventType.CONSENT_DECREE_ORDER,
    EventType.CONSENT_ORDER: ConsolidatedEventType.CONSENT_DECREE_ORDER,
    EventType.DECLARATION: ConsolidatedEventType.AFFIDAVIT_DECLARATION,
    EventType.DECISION: ConsolidatedEventType.DECISION,
    EventType.EXHIBIT: ConsolidatedEventType.APPENDIX_EXHIBIT_SUPPLEMENT,
    EventType.EXPERT_REPORT: ConsolidatedEventType.EXPERT_REPORT,
    EventType.FEDERAL_REGISTER_NOTICE: ConsolidatedEventType.NOTICE,
    EventType.FINAL_DECISION: ConsolidatedEventType.DECISION,
    EventType.FINDINGS_AND_RECOMMENDATIONS: ConsolidatedEventType.REPORT_AND_RECOMMENDATION,
    EventType.FINDINGS_OF_FACT_AND_CONCLUSIONS_OF_LAW: ConsolidatedEventType.DECISION,
    EventType.JOINT_PROPOSED_REMEDY: ConsolidatedEventType.SETTLEMENT,
    EventType.JOINDER: ConsolidatedEventType.MOTION,
    EventType.JUDGMENT: ConsolidatedEventType.DECISION,
    EventType.LETTER: ConsolidatedEventType.LETTER,
    EventType.MEMORANDUM: ConsolidatedEventType.DECISION,
    EventType.MEMORANDUM_AND_ORDER: ConsolidatedEventType.DECISION,
    EventType.MEMORANDUM_DECISION: ConsolidatedEventType.DECISION,
    EventType.MEMORANDUM_OF_DECISION: ConsolidatedEventType.DECISION,
    EventType.MEMORANDUM_OF_LAW: ConsolidatedEventType.BRIEF,
    EventType.MEMORANDUM_OPINION: ConsolidatedEventType.DECISION,
    EventType.MEMORANDUM_OPINION_AND_ORDER: ConsolidatedEventType.DECISION,
    EventType.MINUTE_ORDER: ConsolidatedEventType.DECISION,
    EventType.MINUTE_PROCEEDINGS: ConsolidatedEventType.TRANSCRIPT,
    EventType.MOTION: ConsolidatedEventType.MOTION,
    EventType.MOTION_FOR_SUMMARY_JUDGMENT: ConsolidatedEventType.MOTION_FOR_SUMMARY_JUDGMENT,
    EventType.MOTION_TO_DISMISS: ConsolidatedEventType.MOTION_TO_DISMISS,
    EventType.MOTION_TO_INTERVENE: ConsolidatedEventType.MOTION_TO_INTERVENE,
    EventType.NOTICE: ConsolidatedEventType.NOTICE,
    EventType.NOTICE_OF_APPEAL: ConsolidatedEventType.APPEAL,
    EventType.NOTICE_OF_INTENT: ConsolidatedEventType.NOTICE,
    EventType.NOTICE_OF_INTENT_TO_SUE: ConsolidatedEventType.NOTICE_OF_INTENT_TO_SUE,
    EventType.NOTICE_OF_REMOVAL: ConsolidatedEventType.NOTICE_OF_REMOVAL,
    EventType.NOTICE_OF_RULING: ConsolidatedEventType.NOTICE,
    EventType.NOTICE_OF_VOLUNTARY_DISMISSAL: ConsolidatedEventType.NOTICE_OF_VOLUNTARY_DISMISSAL,
    EventType.NOTIFICATION: ConsolidatedEventType.NOTICE,
    EventType.OBJECTION: ConsolidatedEventType.OBJECTIONS,
    EventType.OPINION: ConsolidatedEventType.DECISION,
    EventType.OPINION_AND_ORDER: ConsolidatedEventType.DECISION,
    EventType.OPPOSITION: ConsolidatedEventType.OPPOSITION,
    EventType.ORDER: ConsolidatedEventType.DECISION,
    EventType.ORDER_DENYING_PETITION_FOR_REVIEW: ConsolidatedEventType.DECISION,
    EventType.ORDER_LIST: ConsolidatedEventType.DECISION,
    EventType.ORDER_TO_SHOW_CAUSE: ConsolidatedEventType.DECISION,
    EventType.PETITION: ConsolidatedEventType.PETITION,
    EventType.PETITION_FOR_RECONSIDERATION: ConsolidatedEventType.PETITION,
    EventType.PETITION_FOR_REHEARING: ConsolidatedEventType.PETITION_FOR_REHEARING,
    EventType.PETITION_FOR_REVIEW: ConsolidatedEventType.PETITION,
    EventType.PETITION_FOR_RULEMAKING: ConsolidatedEventType.PETITION,
    EventType.PETITION_FOR_WRIT_OF_CERTIORARI: ConsolidatedEventType.PETITION_FOR_WRIT_OF_CERTIORARI,
    EventType.PETITION_FOR_WRIT_OF_MANDATE: ConsolidatedEventType.PETITION,
    EventType.PLEA: ConsolidatedEventType.PLEA,
    EventType.POINTS_OF_CLAIM: ConsolidatedEventType.COMPLAINT,
    EventType.PRESS_RELEASE: ConsolidatedEventType.PRESS_RELEASE,
    EventType.REPLY: ConsolidatedEventType.REPLY,
    EventType.REQUEST: ConsolidatedEventType.REQUEST,
    EventType.REQUEST_FOR_ADMINISTRATIVE_STAY: ConsolidatedEventType.REQUEST,
    EventType.REQUEST_FOR_REHEARING: ConsolidatedEventType.REQUEST,
    EventType.REPORT_AND_RECOMMENDATION: ConsolidatedEventType.REPORT_AND_RECOMMENDATION,
    EventType.RESPONSE: ConsolidatedEventType.RESPONSE,
    EventType.RESPONSE_TO_PETITION_FOR_RULEMAKING: ConsolidatedEventType.RESPONSE,
    EventType.RULING: ConsolidatedEventType.DECISION,
    EventType.SETTLEMENT_AGREEMENT: ConsolidatedEventType.SETTLEMENT_AGREEMENT,
    EventType.STATEMENT: ConsolidatedEventType.STATEMENT,
    EventType.STATEMENT_OF_ISSUES: ConsolidatedEventType.STATEMENT,
    EventType.STATEMENT_OF_REPLY: ConsolidatedEventType.REPLY,
    EventType.STATUS_REPORT: ConsolidatedEventType.STATUS_REPORT,
    EventType.STIPULATION: ConsolidatedEventType.STIPULATION,
    EventType.SUBPOENA: ConsolidatedEventType.SUBPOENA,
    EventType.SUR_REPLY: ConsolidatedEventType.REPLY,
    EventType.SUMMONS: ConsolidatedEventType.COMPLAINT,
    EventType.SUPPLEMENT: ConsolidatedEventType.APPENDIX_EXHIBIT_SUPPLEMENT,
    EventType.TENTATIVE_RULING: ConsolidatedEventType.DECISION,
    EventType.TRANSCRIPT: ConsolidatedEventType.TRANSCRIPT,
    EventType.VERDICT: ConsolidatedEventType.VERDICT,
    EventType.SUBSTITUTION_OF_PARTIES: ConsolidatedEventType.SUBSTITUTION_OF_PARTIES,
}
