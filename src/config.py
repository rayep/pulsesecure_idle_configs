""" ICS Idle Config Parser """

import logging
from .parser import ICSXMLParser
from .xpath import AUTH_SERVERS_ROOT, AUTH_SERVERS
from .xpath import SIGNIN_ROOT, SIGNIN_ADMIN_REALMS, SIGNIN_USER_REALMS
from .xpath import USER_REALMS_ROOT, USER_REALMS, USER_REALMS_AUTHSERVER, USER_REALMS_SECAUTHSERVER, USER_REALMS_DIRSERVER, USER_REALMS_ACCSERVER, USER_REALMS_RMAP
from .xpath import ADMIN_REALMS_ROOT, ADMIN_REALMS, ADMIN_REALMS_AUTHSERVER, ADMIN_REALMS_SECAUTHSERVER, ADMIN_REALMS_DIRSERVER, ADMIN_REALMS_ACCSERVER, ADMIN_REALMS_RMAP
from .xpath import USER_ROLES_ROOT, USER_ROLES, ADMIN_ROLES_ROOT, ADMIN_ROLES
from .xpath import MISC_AOA_ROOT, MISC_IKEV2_ROOT, MISC_AOA_ROLES, MISC_IKEV2_REALMS, MISC_IKEV2_PORTREALM, MISC_IKEV2_PROTOREALM
from .logger import LOGGER

# Console Logging handler.
logging.getLogger(__name__).addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ICSIdleConfig(ICSXMLParser):
    """ICS Idle Config Parser Class"""

    def __init__(self, xml_file) -> None:
        self.log_object = None
        self.results = {}
        super().__init__(xml_file)

    def idle_configs(self):
        """Pipeline method to run all Idle config fetching methods"""
        self.auth_servers()
        self.admin_realms()
        self.user_realms()
        self.signin_urls()
        self.user_roles()
        self.admin_roles()
        self.misc_aoa_roles()
        self.misc_ikev2_realms()

    def get_value(self, root_element: str, element_path: str) -> None:
        """Gets the element value"""
        if self.check_tree(root_element):
            logger.info(LOGGER[self.log_object]['success'])
            self.results[element_path] = self.parse_element(element_path)
        else:
            self.results[element_path] = set()
            logger.warning(LOGGER[self.log_object]['fail'])

    def get_values(self, root_element: str, element_path: list) -> None:
        """Get element values from multiple paths"""
        if isinstance(element_path, list):
            if self.check_tree(root_element):
                logger.info(LOGGER[self.log_object]['success'])
                for elem in element_path:
                    self.results[elem] = self.parse_element(elem)
            else:
                for elem in element_path:
                    self.results[elem] = set()
                logger.warning(LOGGER[self.log_object]['fail'])

    def auth_servers(self) -> None:
        """Parse Total Auth Servers"""
        self.log_object = self.auth_servers.__name__
        self.get_value(
            root_element=AUTH_SERVERS_ROOT,
            element_path=AUTH_SERVERS
        )

    @property
    def total_auth_servers(self) -> set:
        """Get Total Auth Servers"""
        return self.results[AUTH_SERVERS]

    def signin_urls(self) -> None:
        """Parse user & admin realms from signin_policies"""
        self.log_object = self.signin_urls.__name__
        elements = [SIGNIN_USER_REALMS, SIGNIN_ADMIN_REALMS]
        self.get_values(
            root_element=SIGNIN_ROOT,
            element_path=elements
        )

    def user_realms(self) -> None:
        """Parse elements present under user realms section"""
        self.log_object = self.user_realms.__name__
        elements = [
            USER_REALMS,
            USER_REALMS_AUTHSERVER,
            USER_REALMS_SECAUTHSERVER,
            USER_REALMS_DIRSERVER,
            USER_REALMS_ACCSERVER,
            USER_REALMS_RMAP
        ]
        self.get_values(
            root_element=USER_REALMS_ROOT,
            element_path=elements
        )

    @property
    def total_user_realms(self) -> set:
        """Total user realms from realms data"""
        return self.results[USER_REALMS]

    def admin_realms(self) -> None:
        """Parse elements present under Admin realms section"""
        self.log_object = self.admin_realms.__name__
        elements = [
            ADMIN_REALMS,
            ADMIN_REALMS_AUTHSERVER,
            ADMIN_REALMS_SECAUTHSERVER,
            ADMIN_REALMS_DIRSERVER,
            ADMIN_REALMS_ACCSERVER,
            ADMIN_REALMS_RMAP
        ]
        self.get_values(
            root_element=ADMIN_REALMS_ROOT,
            element_path=elements
        )

    @property
    def total_admin_realms(self) -> set:
        """Total Admin realms from realms data"""
        return self.results[ADMIN_REALMS]

    def user_roles(self) -> None:
        """Parse total user roles from roles data"""
        self.log_object = self.user_roles.__name__

        self.get_value(
            root_element=USER_ROLES_ROOT,
            element_path=USER_ROLES
        )

    @property
    def total_user_roles(self) -> set:
        """Get total user role from results dict"""
        return self.results[USER_ROLES]

    def admin_roles(self) -> None:
        """Parse total admin roles from roles data"""
        self.log_object = self.admin_roles.__name__

        self.get_value(
            root_element=ADMIN_ROLES_ROOT,
            element_path=ADMIN_ROLES
        )

    @property
    def total_admin_roles(self) -> set:
        """Get total user role from results dict"""
        return self.results[ADMIN_ROLES]

    def misc_aoa_roles(self) -> None:
        """MISC: AOA Roles"""
        if self.check_tree(MISC_AOA_ROOT):
            logger.info("SUCCESS: (misc)Authorization-Only policy data found.")

            if self.check_tree(MISC_AOA_ROLES):
                logger.info(
                    "SUCCESS: (misc)Authorization-Only policy role mapping found.")
                self.results[MISC_AOA_ROLES] = self.parse_element(
                    MISC_AOA_ROLES)
            else:
                self.results[MISC_AOA_ROLES] = set()
        else:
            self.results[MISC_AOA_ROLES] = set()
            logger.warning(
                "ERROR: (misc)Authorization-Only policy data not found.\
                Roles data might be inaccurate!"
            )

    @property
    def aoa_roles(self) -> set:
        """Gets the AOA roles from result"""
        return self.results[MISC_AOA_ROLES]

    def misc_ikev2_realms(self) -> None:
        """MISC: IKEv2 realms"""
        if self.check_tree(MISC_IKEV2_ROOT):
            logger.info("SUCCESS: (misc)IKEv2 config data found.")

            if self.check_tree(MISC_IKEV2_PORTREALM):
                logger.info("SUCCESS: (misc)IKEv2 Port realm mapping found.")
                self.results[MISC_IKEV2_PORTREALM] = self.parse_element(
                    MISC_IKEV2_PORTREALM)
            else:
                self.results[MISC_IKEV2_PORTREALM] = set()

            if self.check_tree(MISC_IKEV2_PROTOREALM):
                logger.info(
                    "SUCCESS: (misc)IKEv2 Protocol realm mapping found.")
                self.results[MISC_IKEV2_PROTOREALM] = self.parse_element(
                    MISC_IKEV2_PROTOREALM)
            else:
                self.results[MISC_IKEV2_PROTOREALM] = set()

            self.results[MISC_IKEV2_REALMS] = self.results[MISC_IKEV2_PORTREALM].union(
                self.results[MISC_IKEV2_PROTOREALM]
            )  # Union them to get all realms.

        else:
            logger.warning(
                "ERROR: (misc)IKEv2 Config data not found. Realms data might be inaccurate!")
            self.results[MISC_IKEV2_REALMS] = set()

    @property
    def ikev2_realms(self) -> set:
        """IKEv2 Realms configured"""
        return self.results[MISC_IKEV2_REALMS]

    @property
    def idle_user_realms(self) -> set:
        """Idle User realms"""
        return self.total_user_realms.difference(
            self.results[SIGNIN_USER_REALMS],
            self.results[MISC_IKEV2_REALMS]
        )

    @property
    def idle_admin_realms(self) -> set:
        """Idle Admin realms"""
        return self.total_admin_realms.difference(
            self.results[SIGNIN_ADMIN_REALMS]
        )

    @property
    def idle_auth_servers(self) -> set:
        """Idle Auth Servers"""
        return self.total_auth_servers.difference(
            self.results[USER_REALMS_AUTHSERVER],
            self.results[USER_REALMS_SECAUTHSERVER],
            self.results[USER_REALMS_DIRSERVER],
            self.results[USER_REALMS_ACCSERVER],
            self.results[ADMIN_REALMS_AUTHSERVER],
            self.results[ADMIN_REALMS_SECAUTHSERVER],
            self.results[ADMIN_REALMS_DIRSERVER],
            self.results[ADMIN_REALMS_ACCSERVER]
        )

    @property
    def idle_user_roles(self) -> set:
        """Idle User roles"""
        return self.total_user_roles.difference(
            self.results[USER_REALMS_RMAP],
            self.results[MISC_AOA_ROLES]
        )

    @property
    def idle_admin_roles(self) -> set:
        """Idle Admin roles"""
        return self.total_admin_roles.difference(
            self.results[ADMIN_REALMS_RMAP]
        )
