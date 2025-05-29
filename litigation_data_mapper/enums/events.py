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
    OBJECTIONS = "Objections"
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
    SETTLEMENT = "Settlement"
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
    OTHER = "Other"


class DocType(Enum):
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
    NA = "Na"


DOC_TYPE_TO_EVENT_TYPE = {
    DocType.ADMINISTRATIVE_ORDER: EventType.ORDER,
    # DocType.AFFIDAVIT: "Affidavit/Declaration",
    # DocType.AFFIRMATION: "Affidavit/Declaration",
    # DocType.AFFIXED: None,
    # DocType.AMICUS_BRIEF: "Amicus Motion/Brief",
    # DocType.AMICUS_MOTION: "Amicus Motion/Brief",
    DocType.ANSWER: EventType.ANSWER,
    DocType.APPEAL: EventType.APPEAL,
    # DocType.APPENDIX: "Appendix/Exhibit/Supplement",
    DocType.APPLICATION: EventType.APPLICATION,
    DocType.APPLICATION_FOR_ADMINISTRATIVE_STAY: EventType.APPLICATION,
    # DocType.ASSURANCE_OF_DISCONTINUANCE: None,  No longer used
    DocType.BILL_OF_COMPLAINT: EventType.MOTION,
    DocType.BRIEF: EventType.BRIEF,
    DocType.COMPLAINT: EventType.COMPLAINT,
    DocType.CONCILIATION_AGREEMENT: EventType.SETTLEMENT_AGREEMENT,
    # DocType.CONSENT_DECREE: "Consent Decree/Order",
    # DocType.CONSENT_MOTION: "Consent Decree/Order",
    # DocType.CONSENT_ORDER: "Consent Decree/Order",
    # DocType.DECLARATION: "Affidavit/Declaration",
    DocType.DECISION: EventType.DECISION,
    # DocType.EXHIBIT: "Appendix/Exhibit/Supplement",
    DocType.EXPERT_REPORT: EventType.EXPERT_REPORT,
    DocType.FEDERAL_REGISTER_NOTICE: EventType.NOTICE,
    DocType.FILING_YEAR_FOR_ACTION: EventType.FILING_YEAR_FOR_ACTION,
    DocType.FINAL_DECISION: EventType.DECISION,
    # DocType.FINAL_DETERMINATION: None,
    DocType.FINDINGS_AND_RECOMMENDATIONS: EventType.REPORT_AND_RECOMMENDATION,
    DocType.FINDINGS_OF_FACT_AND_CONCLUSIONS_OF_LAW: EventType.DECISION,
    DocType.JOINT_PROPOSED_REMEDY: EventType.SETTLEMENT,
    DocType.JOINDER: EventType.MOTION,
    DocType.JUDGMENT: EventType.DECISION,
    DocType.LETTER: EventType.LETTER,
    # DocType.MEMORANDUM: None,
    DocType.MEMORANDUM_AND_ORDER: EventType.DECISION,
    DocType.MEMORANDUM_DECISION: EventType.DECISION,
    DocType.MEMORANDUM_OF_DECISION: EventType.DECISION,
    DocType.MEMORANDUM_OF_LAW: EventType.BRIEF,
    DocType.MEMORANDUM_OPINION: EventType.DECISION,
    DocType.MEMORANDUM_OPINION_AND_ORDER: EventType.DECISION,
    DocType.MINUTE_ORDER: EventType.DECISION,
    DocType.MINUTE_PROCEEDINGS: EventType.TRANSCRIPT,
    DocType.MOTION: EventType.MOTION,
    DocType.MOTION_FOR_SUMMARY_JUDGMENT: EventType.MOTION_FOR_SUMMARY_JUDGMENT,
    DocType.MOTION_TO_DISMISS: EventType.MOTION_TO_DISMISS,
    DocType.MOTION_TO_INTERVENE: EventType.MOTION_TO_INTERVENE,
    DocType.NOTICE: EventType.NOTICE,
    DocType.NOTICE_OF_APPEAL: EventType.APPEAL,
    DocType.NOTICE_OF_INTENT: EventType.NOTICE,
    DocType.NOTICE_OF_INTENT_TO_SUE: EventType.NOTICE_OF_INTENT_TO_SUE,
    DocType.NOTICE_OF_REMOVAL: EventType.NOTICE_OF_REMOVAL,
    DocType.NOTICE_OF_RULING: EventType.NOTICE,
    DocType.NOTICE_OF_VOLUNTARY_DISMISSAL: EventType.NOTICE_OF_VOLUNTARY_DISMISSAL,
    DocType.NOTIFICATION: EventType.NOTICE,
    DocType.OBJECTION: EventType.OBJECTIONS,
    DocType.OPINION: EventType.DECISION,
    DocType.OPINION_AND_ORDER: EventType.DECISION,
    DocType.OPPOSITION: EventType.OPPOSITION,
    DocType.ORDER: EventType.DECISION,
    DocType.ORDER_DENYING_PETITION_FOR_REVIEW: EventType.DECISION,
    DocType.ORDER_LIST: EventType.DECISION,
    DocType.ORDER_TO_SHOW_CAUSE: EventType.DECISION,
    DocType.PETITION: EventType.PETITION,
    DocType.PETITION_FOR_RECONSIDERATION: EventType.PETITION,
    DocType.PETITION_FOR_REHEARING: EventType.PETITION_FOR_REHEARING,
    DocType.PETITION_FOR_REVIEW: EventType.PETITION,
    DocType.PETITION_FOR_RULEMAKING: EventType.PETITION,
    DocType.PETITION_FOR_WRIT_OF_CERTIORARI: EventType.PETITION_FOR_WRIT_OF_CERTIORARI,
    DocType.PETITION_FOR_WRIT_OF_MANDATE: EventType.PETITION,
    DocType.PLEA: EventType.PLEA,
    DocType.POINTS_OF_CLAIM: EventType.COMPLAINT,
    DocType.PRESS_RELEASE: EventType.PRESS_RELEASE,
    DocType.REPLY: EventType.REPLY,
    DocType.REQUEST: EventType.REQUEST,
    DocType.REQUEST_FOR_ADMINISTRATIVE_STAY: EventType.REQUEST,
    DocType.REQUEST_FOR_REHEARING: EventType.REQUEST,
    DocType.REPORT_AND_RECOMMENDATION: EventType.REPORT_AND_RECOMMENDATION,
    DocType.RESPONSE: EventType.RESPONSE,
    DocType.RESPONSE_TO_PETITION_FOR_RULEMAKING: EventType.RESPONSE,
    DocType.RULING: EventType.DECISION,
    DocType.SETTLEMENT_AGREEMENT: EventType.SETTLEMENT_AGREEMENT,
    DocType.STATEMENT: EventType.STATEMENT,
    DocType.STATEMENT_OF_ISSUES: EventType.STATEMENT,
    DocType.STATEMENT_OF_REPLY: EventType.REPLY,
    DocType.STATUS_REPORT: EventType.STATUS_REPORT,
    DocType.STIPULATION: EventType.STIPULATION,
    DocType.SUBPOENA: EventType.SUBPOENA,
    DocType.SUR_REPLY: EventType.REPLY,
    DocType.SUMMONS: EventType.COMPLAINT,
    # DocType.SUPPLEMENT: "Appendix/Exhibit/Supplement",
    DocType.TENTATIVE_RULING: EventType.DECISION,
    DocType.TRANSCRIPT: EventType.TRANSCRIPT,
    DocType.VERDICT: EventType.VERDICT,
    DocType.NA: EventType.OTHER,
}

# TODO : ADD Settlement to Event Type in data migrations
# TODO: Change objection to objections in data migrations
