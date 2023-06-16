from fastapi import FastAPI

from controllers.approvals import (
    CreateApprovalFlowController,
    CreateApprovalRequestController,
    ProcessApprovalRequestController,
    ApprovalRequestDetailsController,
    GetSmApproverListController,
    GetApprovalFlowListForSMController,
    UpdateApprovalFlowController,
)
from controllers.approvals.approvals_access import ApprovalsAccessController
from routers import (
    ApprovalFlowRoutesGroup,
    ApprovalRequestRoutesGroup,
    ApproverRoutesGroup,
    InternalRoutesGroup
)


class RouteController:
    def __init__(
        self,
        app: FastAPI,
    ):
        create_approval_flow_controller = CreateApprovalFlowController(
        )

        get_sm_approval_flow_list_controller = GetApprovalFlowListForSMController(
        )

        update_approval_flow_controller = UpdateApprovalFlowController()

        approval_flow_router = ApprovalFlowRoutesGroup(
            create_approval_flow_controller_route=create_approval_flow_controller,
            get_sm_approval_flow_list_controller_route=get_sm_approval_flow_list_controller,
            update_approval_flow_controller_route=update_approval_flow_controller,
        ).router

        app.include_router(
            prefix=ApprovalFlowRoutesGroup.prefix, router=approval_flow_router
        )

        create_approval_request_controller = CreateApprovalRequestController(
        )

        process_approval_request_controller = ProcessApprovalRequestController(
        )

        approval_request_details_controller = ApprovalRequestDetailsController(
        )

        approval_request_router = ApprovalRequestRoutesGroup(
            create_approval_request_controller_route=create_approval_request_controller,
            process_approval_request_controller_route=process_approval_request_controller,
            approval_request_details_controller_route=approval_request_details_controller,
        ).router

        app.include_router(
            prefix=ApprovalRequestRoutesGroup.prefix, router=approval_request_router
        )

        get_sm_approver_list_controller = GetSmApproverListController()
        approval_access_controller = ApprovalsAccessController()

        approver_router = ApproverRoutesGroup(
            get_sm_approver_list_controller_route=get_sm_approver_list_controller,
            approvals_access_controller=approval_access_controller
        ).router

        app.include_router(prefix=ApproverRoutesGroup.prefix, router=approver_router)

        internal_routes_group = InternalRoutesGroup(
            approval_request_details_controller=approval_request_details_controller
        ).router

        app.include_router(
            prefix=InternalRoutesGroup.prefix, router=internal_routes_group
        )