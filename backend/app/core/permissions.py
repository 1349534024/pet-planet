from enum import StrEnum


class RoleCode(StrEnum):
    user = "user"
    merchant = "merchant"
    operator = "operator"
    admin = "admin"


DEFAULT_ROLE_DEFINITIONS: dict[str, str] = {
    RoleCode.user.value: "普通用户",
    RoleCode.merchant.value: "商家",
    RoleCode.operator.value: "运营人员",
    RoleCode.admin.value: "管理员",
}


def normalize_role_codes(role_codes: list[str]) -> list[str]:
    return sorted({role_code.strip().lower() for role_code in role_codes if role_code.strip()})
