"""Script to seed comprehensive test data for development and testing purposes."""

import sys
from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.core.security import hash_password
from productivity_tracker.database import SessionLocal
from productivity_tracker.database.entities import (
    Department,
    Organization,
    Role,
    Team,
    User,
)


class TestDataSeeder:
    """Seed test data for the productivity tracker application."""

    def __init__(self, db: Session, superuser_id: str):
        self.db = db
        self.superuser_id = UUID(superuser_id)
        self.superuser = None
        self.created_users: list[User] = []
        self.created_orgs: list[Organization] = []
        self.created_depts: list[Department] = []
        self.created_teams: list[Team] = []

    def verify_superuser(self) -> bool:
        """Verify that the provided superuser ID exists and is valid."""
        self.superuser = self.db.query(User).filter(User.id == self.superuser_id).first()
        if not self.superuser:
            print(f"❌ Superuser with ID {self.superuser_id} not found.")
            return False
        if not self.superuser.is_superuser:
            print(f"❌ User {self.superuser.username} is not a superuser.")
            return False
        print(f"✅ Verified superuser: {self.superuser.username} ({self.superuser.email})")
        return True

    def create_users(self):
        """Create test users with various roles."""
        print("\n📝 Creating test users...")

        # Get roles from database
        roles = {role.name: role for role in self.db.query(Role).all()}

        if not roles:
            print("⚠️  No roles found. Please run seed_rbac.py first!")
            return

        users_data = [
            # Organization managers
            {
                "username": "alice_smith",
                "email": "alice.smith@techcorp.com",
                "password": "password123",
                "first_name": "Alice",
                "last_name": "Smith",
                "roles": ["organization_manager"],
            },
            {
                "username": "bob_johnson",
                "email": "bob.johnson@innovate.com",
                "password": "password123",
                "first_name": "Bob",
                "last_name": "Johnson",
                "roles": ["organization_manager"],
            },
            # Department managers
            {
                "username": "carol_williams",
                "email": "carol.williams@techcorp.com",
                "password": "password123",
                "first_name": "Carol",
                "last_name": "Williams",
                "roles": ["department_manager"],
            },
            {
                "username": "david_brown",
                "email": "david.brown@techcorp.com",
                "password": "password123",
                "first_name": "David",
                "last_name": "Brown",
                "roles": ["department_manager"],
            },
            {
                "username": "emily_davis",
                "email": "emily.davis@innovate.com",
                "password": "password123",
                "first_name": "Emily",
                "last_name": "Davis",
                "roles": ["department_manager"],
            },
            # Team leads
            {
                "username": "frank_miller",
                "email": "frank.miller@techcorp.com",
                "password": "password123",
                "first_name": "Frank",
                "last_name": "Miller",
                "roles": ["team_lead"],
            },
            {
                "username": "grace_wilson",
                "email": "grace.wilson@techcorp.com",
                "password": "password123",
                "first_name": "Grace",
                "last_name": "Wilson",
                "roles": ["team_lead"],
            },
            {
                "username": "henry_moore",
                "email": "henry.moore@techcorp.com",
                "password": "password123",
                "first_name": "Henry",
                "last_name": "Moore",
                "roles": ["team_lead"],
            },
            {
                "username": "iris_taylor",
                "email": "iris.taylor@innovate.com",
                "password": "password123",
                "first_name": "Iris",
                "last_name": "Taylor",
                "roles": ["team_lead"],
            },
            # Regular users
            {
                "username": "jack_anderson",
                "email": "jack.anderson@techcorp.com",
                "password": "password123",
                "first_name": "Jack",
                "last_name": "Anderson",
                "roles": ["user"],
            },
            {
                "username": "kate_thomas",
                "email": "kate.thomas@techcorp.com",
                "password": "password123",
                "first_name": "Kate",
                "last_name": "Thomas",
                "roles": ["user"],
            },
            {
                "username": "liam_jackson",
                "email": "liam.jackson@techcorp.com",
                "password": "password123",
                "first_name": "Liam",
                "last_name": "Jackson",
                "roles": ["user"],
            },
            {
                "username": "mia_white",
                "email": "mia.white@techcorp.com",
                "password": "password123",
                "first_name": "Mia",
                "last_name": "White",
                "roles": ["user"],
            },
            {
                "username": "noah_harris",
                "email": "noah.harris@innovate.com",
                "password": "password123",
                "first_name": "Noah",
                "last_name": "Harris",
                "roles": ["user"],
            },
            {
                "username": "olivia_martin",
                "email": "olivia.martin@innovate.com",
                "password": "password123",
                "first_name": "Olivia",
                "last_name": "Martin",
                "roles": ["user"],
            },
            # Viewers
            {
                "username": "peter_garcia",
                "email": "peter.garcia@techcorp.com",
                "password": "password123",
                "first_name": "Peter",
                "last_name": "Garcia",
                "roles": ["viewer"],
            },
            {
                "username": "quinn_rodriguez",
                "email": "quinn.rodriguez@innovate.com",
                "password": "password123",
                "first_name": "Quinn",
                "last_name": "Rodriguez",
                "roles": ["viewer"],
            },
            # Admin
            {
                "username": "rachel_admin",
                "email": "rachel.admin@techcorp.com",
                "password": "password123",
                "first_name": "Rachel",
                "last_name": "Chen",
                "roles": ["admin"],
            },
        ]

        for user_data in users_data:
            # Check if user already exists
            existing = (
                self.db.query(User)
                .filter(
                    (User.username == user_data["username"]) | (User.email == user_data["email"])
                )
                .first()
            )
            if existing:
                print(f"  ⚠️  User {user_data['username']} already exists, skipping...")
                self.created_users.append(existing)
                continue

            # Create user
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                is_active=True,
                is_superuser=False,
            )

            # Assign roles
            for role_name in user_data["roles"]:
                role = roles.get(role_name)
                if role:
                    user.roles.append(role)

            self.db.add(user)
            self.created_users.append(user)
            print(f"  ✅ Created user: {user.username} ({', '.join(user_data['roles'])})")

        self.db.commit()
        print(f"\n✅ Created {len(self.created_users)} users")

    def create_organizations(self):
        """Create test organizations."""
        print("\n🏢 Creating organizations...")

        orgs_data = [
            {
                "name": "TechCorp Industries",
                "slug": "techcorp",
                "description": "Leading technology solutions provider specializing in enterprise software",
                "members": [
                    "alice_smith",
                    "carol_williams",
                    "david_brown",
                    "frank_miller",
                    "grace_wilson",
                    "henry_moore",
                    "jack_anderson",
                    "kate_thomas",
                    "liam_jackson",
                    "mia_white",
                    "peter_garcia",
                    "rachel_admin",
                ],
            },
            {
                "name": "Innovate Solutions",
                "slug": "innovate",
                "description": "Innovative startup focused on AI and machine learning solutions",
                "members": [
                    "bob_johnson",
                    "emily_davis",
                    "iris_taylor",
                    "noah_harris",
                    "olivia_martin",
                    "quinn_rodriguez",
                ],
            },
        ]

        for org_data in orgs_data:
            # Check if org already exists
            existing = (
                self.db.query(Organization)
                .filter(
                    (Organization.slug == org_data["slug"])
                    | (Organization.name == org_data["name"])
                )
                .first()
            )
            if existing:
                print(f"  ⚠️  Organization {org_data['name']} already exists, skipping...")
                self.created_orgs.append(existing)
                continue

            # Create organization
            org = Organization(
                name=org_data["name"],
                slug=org_data["slug"],
                description=org_data["description"],
            )

            # Add members
            for username in org_data["members"]:
                user = self.db.query(User).filter(User.username == username).first()
                if user:
                    org.members.append(user)

            # Add superuser as member
            if self.superuser and self.superuser not in org.members:
                org.members.append(self.superuser)

            self.db.add(org)
            self.created_orgs.append(org)
            print(f"  ✅ Created organization: {org.name} ({len(org_data['members'])} members)")

        self.db.commit()
        print(f"\n✅ Created {len(self.created_orgs)} organizations")

    def create_departments(self):
        """Create departments within organizations."""
        print("\n🏛️  Creating departments...")

        # Get organizations
        techcorp = self.db.query(Organization).filter(Organization.slug == "techcorp").first()
        innovate = self.db.query(Organization).filter(Organization.slug == "innovate").first()

        if not techcorp or not innovate:
            print("❌ Organizations not found. Cannot create departments.")
            return

        depts_data = [
            # TechCorp departments
            {
                "name": "Engineering",
                "description": "Software development and engineering teams",
                "organization": techcorp,
            },
            {
                "name": "Product Management",
                "description": "Product strategy and roadmap planning",
                "organization": techcorp,
            },
            {
                "name": "Sales & Marketing",
                "description": "Customer acquisition and market expansion",
                "organization": techcorp,
            },
            # Innovate departments
            {
                "name": "Research & Development",
                "description": "AI and ML research initiatives",
                "organization": innovate,
            },
            {
                "name": "Operations",
                "description": "Business operations and customer success",
                "organization": innovate,
            },
        ]

        for dept_data in depts_data:
            # Check if department exists
            existing = (
                self.db.query(Department)
                .filter(
                    Department.name == dept_data["name"],
                    Department.organization_id == dept_data["organization"].id,
                )
                .first()
            )
            if existing:
                print(f"  ⚠️  Department {dept_data['name']} already exists, skipping...")
                self.created_depts.append(existing)
                continue

            dept = Department(
                name=dept_data["name"],
                description=dept_data["description"],
                organization_id=dept_data["organization"].id,
            )
            self.db.add(dept)
            self.created_depts.append(dept)
            print(f"  ✅ Created department: {dept.name} in {dept_data['organization'].name}")

        self.db.commit()
        print(f"\n✅ Created {len(self.created_depts)} departments")

    def create_teams(self):
        """Create teams within departments."""
        print("\n👥 Creating teams...")

        # Get departments
        engineering = (
            self.db.query(Department)
            .join(Organization)
            .filter(Department.name == "Engineering", Organization.slug == "techcorp")
            .first()
        )
        product = (
            self.db.query(Department)
            .join(Organization)
            .filter(Department.name == "Product Management", Organization.slug == "techcorp")
            .first()
        )
        sales = (
            self.db.query(Department)
            .join(Organization)
            .filter(Department.name == "Sales & Marketing", Organization.slug == "techcorp")
            .first()
        )
        rnd = (
            self.db.query(Department)
            .join(Organization)
            .filter(Department.name == "Research & Development", Organization.slug == "innovate")
            .first()
        )
        ops = (
            self.db.query(Department)
            .join(Organization)
            .filter(Department.name == "Operations", Organization.slug == "innovate")
            .first()
        )

        if not all([engineering, product, sales, rnd, ops]):
            print("❌ Not all departments found. Cannot create teams.")
            return

        teams_data = [
            # Engineering teams
            {
                "name": "Backend Team",
                "description": "API and backend services development",
                "department": engineering,
                "lead": "frank_miller",
                "members": ["frank_miller", "jack_anderson", "kate_thomas"],
            },
            {
                "name": "Frontend Team",
                "description": "User interface and web application development",
                "department": engineering,
                "lead": "grace_wilson",
                "members": ["grace_wilson", "liam_jackson", "mia_white"],
            },
            # Product teams
            {
                "name": "Product Strategy",
                "description": "Product vision and strategic planning",
                "department": product,
                "lead": "henry_moore",
                "members": ["henry_moore", "peter_garcia"],
            },
            # R&D teams
            {
                "name": "AI Research",
                "description": "Artificial intelligence and machine learning research",
                "department": rnd,
                "lead": "iris_taylor",
                "members": ["iris_taylor", "noah_harris", "olivia_martin"],
            },
        ]

        for team_data in teams_data:
            # Check if team exists
            existing = (
                self.db.query(Team)
                .filter(
                    Team.name == team_data["name"],
                    Team.department_id == team_data["department"].id,
                )
                .first()
            )
            if existing:
                print(f"  ⚠️  Team {team_data['name']} already exists, skipping...")
                self.created_teams.append(existing)
                continue

            # Get team lead
            lead = self.db.query(User).filter(User.username == team_data["lead"]).first()

            team = Team(
                name=team_data["name"],
                description=team_data["description"],
                department_id=team_data["department"].id,
                lead_id=lead.id if lead else None,
            )

            # Add members
            for username in team_data["members"]:
                user = self.db.query(User).filter(User.username == username).first()
                if user:
                    team.members.append(user)

            self.db.add(team)
            self.created_teams.append(team)
            print(
                f"  ✅ Created team: {team.name} in {team_data['department'].name} "
                f"(Lead: {team_data['lead']}, {len(team_data['members'])} members)"
            )

        self.db.commit()
        print(f"\n✅ Created {len(self.created_teams)} teams")

    def print_summary(self):
        """Print a summary of all created test data."""
        print("\n" + "=" * 80)
        print("TEST DATA SEEDING SUMMARY")
        print("=" * 80)
        print(f"\n👤 Users created: {len(self.created_users)}")
        print(f"🏢 Organizations created: {len(self.created_orgs)}")
        print(f"🏛️  Departments created: {len(self.created_depts)}")
        print(f"👥 Teams created: {len(self.created_teams)}")

        print("\n📊 ORGANIZATIONAL HIERARCHY:")
        print("-" * 80)

        for org in self.created_orgs:
            print(f"\n🏢 {org.name} ({org.slug})")
            print(f"   Members: {org.members.count()}")

            for dept in org.departments:
                print(f"   └─ 🏛️  {dept.name}")
                print(f"      {dept.description}")

                for team in dept.teams:
                    lead_name = (
                        f"{team.lead.first_name} {team.lead.last_name}" if team.lead else "No lead"
                    )
                    print(f"      └─ 👥 {team.name} (Lead: {lead_name})")
                    print(f"         Members: {team.members.count()}")

        print("\n" + "=" * 80)
        print("✅ TEST DATA SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📝 Default password for all test users: password123")
        print("⚠️  Remember to change passwords in production!\n")

    def seed(self):
        """Main seeding method."""
        try:
            if not self.verify_superuser():
                return False

            self.create_users()
            self.create_organizations()
            self.create_departments()
            self.create_teams()
            self.print_summary()

            return True

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            import traceback

            traceback.print_exc()
            self.db.rollback()
            return False


def seed_test_data(superuser_id: str):
    """Seed test data with the given superuser ID."""
    db = SessionLocal()
    try:
        seeder = TestDataSeeder(db, superuser_id)
        success = seeder.seed()
        return 0 if success else 1
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "=" * 80)
        print("SEED TEST DATA")
        print("=" * 80)
        print("\nUsage: python seed_test_data.py <superuser_id>")
        print("\nExample:")
        print('  python seed_test_data.py "ad9c3024-8c65-4ec9-a2d8-0347f8106f0d"')
        print("\n" + "=" * 80 + "\n")
        sys.exit(1)

    superuser_id = sys.argv[1]
    sys.exit(seed_test_data(superuser_id))
