# Task 10 --- HR Chatbot Memory and Permissions

**Project:** CortexHR --- Employee ML Project\
**Task:** 10\
**Report file:** `reports/task10_chatbot_memory_permissions_report.md`\
**Status:** Dialogue acceptance suite passed; security and memory checks
executed in the Task 10 notebook.

------------------------------------------------------------------------

## 1. Executive Summary

Task 10 extends the existing HR FAQ chatbot with authenticated employee
interactions, role-based authorization, session-scoped conversational
memory, follow-up intent handling, and integration with the supplied
mock HR service.

The implementation preserves the earlier chatbot and API work while
adding controls around employee identity and access to HR information.
Authentication is based on the `X-Demo-User` request header. The
employee identity and role are resolved against the trusted demo-user
data and the mock HR service; a role supplied in the request body is not
treated as authoritative.

The supplied Task 10 dialogue acceptance dataset contains 12 dialogues
and 28 turns. The final dialogue test run reported:

  Measure                       Result
  ---------------------- -------------
  Total dialogue turns              28
  Passed                            28
  Failed                             0
  Errors                             0
  Intent accuracy          **100.00%**

The notebook also includes security checks for salary privacy,
request-body role spoofing, authentication requirements, and
authorization of a genuine HR demo identity. Slot extraction and
session-memory assertions are included as well.

## 2. Objectives

The Task 10 implementation and validation address the following
objectives:

1.  Maintain conversational context across multiple turns within a
    session.
2.  Extract and reuse relevant slots such as month, employee,
    department, and job title.
3.  Authenticate demo users through a trusted employee identifier.
4.  Resolve the user's role from trusted demo-user records rather than
    request-body input.
5.  Enforce intent-level login and role requirements configured in
    `data/chatbot_responses.csv`.
6.  Protect employee-specific information and refuse requests for
    another employee's salary.
7.  Use the supplied mock HR service for supported employee and HR data
    retrieval.
8.  Validate the supplied dialogue scenarios and security conditions.

## 3. Project Components

The Task 10 work builds on the existing CortexHR project structure.

  -----------------------------------------------------------------------------------------
  Component                                             Responsibility
  ----------------------------------------------------- -----------------------------------
  `05_Starter/api_skeleton/app/main.py`                 FastAPI application, chat endpoint,
                                                        service dispatch and follow-up
                                                        handling

  `05_Starter/api_skeleton/app/chatbot_service.py`      Existing intent classifier, FAQ
                                                        retrieval, Task 10 intent rules and
                                                        salary privacy checks

  `05_Starter/api_skeleton/app/permission_service.py`   Demo-user resolution and intent
                                                        authorization

  `05_Starter/api_skeleton/app/memory_service.py`       Slot extraction and session-scoped
                                                        memory

  `05_Starter/mock_services/mock_server.py`             Supplied mock HR API

  `05_Starter/mock_services/mock_data/`                 Demo users and mock employee,
                                                        leave, attendance, payslip and
                                                        holiday data

  `data/chatbot_dialogues.csv`                          Supplied multi-turn dialogue
                                                        acceptance dataset

  `data/chatbot_responses.csv`                          Intent configuration, login
                                                        requirements, allowed roles,
                                                        service mappings and failure
                                                        messages

  `notebooks/09_chatbot_memory_permissions.ipynb`       Task 10 validation notebook
  -----------------------------------------------------------------------------------------

The existing Task 9 chatbot classifier and Task 8 API functionality are
retained. Task 10 adds the conversational and authorization layer around
the existing application.

## 4. Authentication and Identity Resolution

The chat endpoint accepts the `X-Demo-User` header as the demo employee
identifier.

The permission service uses the trusted `demo_users.csv` data to
identify the account and its configured role. It also validates the
identity through the mock HR employee-profile endpoint. If the supplied
identity cannot be validated, the request is rejected rather than being
treated as an authenticated user.

The request-body `user_role` field is not used as the source of
authorization. This prevents a user with an employee account from
obtaining HR privileges by submitting a body value such as
`user_role="HR"`.

The effective role is derived from the trusted demo-user record.

## 5. Intent Authorization and Policy Enforcement

Intent rules are loaded from `data/chatbot_responses.csv`. The
configuration contains fields for:

-   `requires_login`
-   `allowed_roles`
-   `backend_or_service_call`
-   `on_failure`
-   `policy_note`

The permission service checks whether the intent is known, whether the
user is authenticated when required, and whether the trusted role is
included in the configured allowed roles.

The explicit `REFUSE` service policy for `salary_of_other` is denied.
Salary privacy checks in the chatbot also take precedence over FAQ
retrieval so that a salary request about another named employee is not
answered using an unrelated FAQ match.

Employee-specific service requests use the authenticated employee
identity and the mock service's `me` routes. The conversational
employee-name slot is not used to change the authenticated identity for
personal HR-data requests.

## 6. Session Memory and Slot Extraction

The memory service extracts supported entities from each message,
including:

-   **Month:** named months, year-qualified months, numeric `YYYY-MM`
    values, and relative month phrases.
-   **Employee:** names loaded from the supplied `employees.csv` file.
-   **Department:** the configured department names used by the supplied
    Task 10 scenarios.
-   **Job title:** the configured job titles used by the supplied Task
    10 scenarios.

Memory is keyed by both `session_id` and authenticated `employee_id`.
This scopes conversation state to the authenticated employee's session
and prevents a different employee from reading the same session's stored
slots.

The authenticated employee identifier is stored separately from
extracted conversational entities. This distinction is important:
mentioning another employee in a message does not change the identity
under which private HR service calls are made.

The dialogue tests include follow-up turns such as a request for another
leave type, a department change in an attrition query, a payroll-details
follow-up, a different job title for a salary-band question, and a
narrowed headcount query.

## 7. Mock HR Service Integration

The supplied mock HR server provides the following routes used by the
application:

  -------------------------------------------------------------------------------
  Method                  Route                           Purpose
  ----------------------- ------------------------------- -----------------------
  GET                     `/api/v1/holidays`              Retrieve the holiday
                                                          list

  GET                     `/api/v1/employees/me`          Retrieve the
                                                          authenticated employee
                                                          profile

  GET                     `/api/v1/employees/me/team`     Retrieve the employee's
                                                          team

  GET                     `/api/v1/leave/balance`         Retrieve the
                                                          authenticated
                                                          employee's leave
                                                          balances

  GET                     `/api/v1/leave/requests`        Retrieve the
                                                          authenticated
                                                          employee's leave
                                                          requests

  GET                     `/api/v1/payslips/me/{month}`   Retrieve the
                                                          authenticated
                                                          employee's payslip for
                                                          a month

  GET                     `/api/v1/attendance/summary`    Retrieve the
                                                          authenticated
                                                          employee's monthly
                                                          attendance summary
  -------------------------------------------------------------------------------

The implementation uses the supplied service's authenticated `me`
endpoints for employee-owned records. The notebook includes direct
checks of these mock routes and records their HTTP status and response
details.

### Backend capability boundary

The response configuration also references analytics capabilities such
as unusual-attendance anomaly analysis, salary-band recommendations,
attrition-risk analytics, headcount forecasting, payroll anomaly
analysis, and resume scoring. These are not all exposed as routes by the
supplied mock HR server.

Where the required analytics backend is unavailable, the application
must return its configured failure response. It must not fabricate an
anomaly score, salary recommendation, attrition result, headcount
forecast, payroll finding, or resume score. The successful dialogue
intent match for these scenarios validates intent recognition and
follow-up handling; it does not by itself establish that an unavailable
analytics computation was performed.

## 8. Dialogue Acceptance Testing

The supplied `data/chatbot_dialogues.csv` dataset was executed through
the FastAPI `/v1/chat` endpoint. Each dialogue used a distinct session
ID, and turns within the same dialogue reused that session.

The final test output reported:

  Metric                  Result
  ---------------- -------------
  Dialogue IDs                12
  Total turns                 28
  Passed turns                28
  Failed turns                 0
  Request errors               0
  Accuracy           **100.00%**

All expected intents in DLG-01 through DLG-12 matched the actual
returned intents in the final run.

The test runner saved detailed turn-level results to:

`reports/task10_dialogue_test_results.csv`

The notebook also saves a compact summary to:

`reports/task10_dialogue_test_summary.csv`

## 9. Security and Memory Validation

The Task 10 notebook includes the following checks:

  -----------------------------------------------------------------------
  Test                                Expected behavior
  ----------------------------------- -----------------------------------
  Other employee salary request       Refuse disclosure and return
                                      `salary_of_other`

  Request-body role spoofing          An employee submitting
                                      `user_role="HR"` remains an
                                      employee and is denied HR-only
                                      access

  Missing authentication              A protected leave-balance request
                                      is denied without `X-Demo-User`

  Genuine HR identity                 A trusted HR demo identity passes
                                      the role-authorization check for an
                                      HR-only intent

  Slot extraction                     Month, employee, department and
                                      job-title examples are extracted

  Session memory                      Authenticated identity and updated
                                      conversational slots are retained
                                      in the correct session
  -----------------------------------------------------------------------

The notebook records the security outcomes in:

`reports/task10_security_test_results.csv`

It also records direct mock-service route checks in:

`reports/task10_mock_service_route_checks.csv`

The notebook's final validation cell asserts the dialogue acceptance
results, security checks, and memory assertions. The user confirmed that
all notebook cells executed.

## 10. Notebook and Evidence Files

The Task 10 notebook is:

`notebooks/09_chatbot_memory_permissions.ipynb`

The notebook is organized to: 1. Locate the project and load the
supplied datasets. 2. Verify demo identities and service connectivity.
3. Execute all 12 supplied dialogues. 4. Assert the expected 28-turn
acceptance result. 5. Run salary privacy, role-spoofing, authentication,
and HR authorization checks. 6. Test slot extraction and session memory.
7. Check the supplied mock HR service routes. 8. Save test evidence
under `reports/`.

Expected evidence files:

  ------------------------------------------------------------------------------------
  File                                             Contents
  ------------------------------------------------ -----------------------------------
  `reports/task10_dialogue_test_results.csv`       Turn-level expected and actual
                                                   intent results

  `reports/task10_dialogue_test_summary.csv`       Overall dialogue test totals and
                                                   accuracy

  `reports/task10_security_test_results.csv`       Security test outcomes

  `reports/task10_mock_service_route_checks.csv`   Mock service endpoint status checks
  ------------------------------------------------------------------------------------

These evidence files are generated when the corresponding notebook cells
run successfully.

## 11. Limitations and Notes

1.  The mock HR server is a demonstration service backed by supplied CSV
    data, not a production HR platform.
2.  Availability of a payslip or attendance record depends on the months
    and employee records present in the mock datasets.
3.  The supplied mock server exposes seven HR data routes. Analytics
    intents that reference services not implemented in the available
    backend must use the configured failure response.
4.  The 100% dialogue accuracy figure measures expected-intent matching
    across the 28 supplied turns. It is not a measure of model quality
    on an independent production dataset, nor does it prove that
    unavailable analytics services produced results.
5.  The in-memory session store is suitable for the task's demonstration
    and test workflow. A production deployment would need an
    appropriately secured, persistent session store and operational
    controls.

## 12. Conclusion

Task 10 adds session-aware conversational behavior and permission
enforcement to the existing CortexHR HR chatbot. Authentication is based
on a trusted demo identity, role permissions are driven by the supplied
intent configuration, and session memory is scoped by session and
authenticated employee. Employee-specific HR data is requested through
authenticated `me` routes, while requests for another employee's salary
are refused.

The final supplied dialogue acceptance run achieved **28 passed out of
28 turns (100.00% intent accuracy), with zero failures and zero request
errors**. The notebook also contains security, slot-extraction,
session-memory, and mock-service validation, with evidence saved under
the project's `reports/` directory.

------------------------------------------------------------------------

**Task 10 report --- CortexHR Employee ML Project**
