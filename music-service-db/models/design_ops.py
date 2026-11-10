from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Employee(SQLModel, table=True):
    __tablename__ = "employees"
    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="roles.id", index=True)
    name: str = Field(max_length=150)
    email: str = Field(unique=True, max_length=255)

    role: Optional["Role"] = Relationship(back_populates="employees")
    owned_assets: List["Asset"] = Relationship(back_populates="owner")
    owned_projects: List["DesignProject"] = Relationship(back_populates="owner")
    authored_versions: List["AssetVersion"] = Relationship(back_populates="author")
    approvals: List["Approval"] = Relationship(back_populates="reviewer")


class DesignProject(SQLModel, table=True):
    __tablename__ = "design_projects"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=150)
    owner_id: Optional[int] = Field(default=None, foreign_key="employees.id")

    owner: Optional[Employee] = Relationship(back_populates="owned_projects")
    assets: List["Asset"] = Relationship(back_populates="project")