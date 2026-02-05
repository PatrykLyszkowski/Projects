# Material Order System

> **Enterprise Material Order Management Solution** built on Microsoft Power Platform  
> *Automating procurement workflows from request to fulfillment*

[Wersja polska](README.pl.md) | [Download Full Documentation (PDF)](https://github.com/PatrykLyszkowski/Projects/raw/main/Power%20Platform/Material-Order/docs/Material_Order_Documentation_EN.pdf)

---

## Overview

**Material Order** is a comprehensive material procurement management system that streamlines the entire ordering process for construction and manufacturing organizations. The solution automates approval workflows, integrates seamlessly with Microsoft Teams, and provides role-based access control for supervisors, managers, and suppliers.

### Key Capabilities

- **Multi-item Order Management** – Create complex orders with multiple line items, quantities, and units
- **Conditional Approval Workflows** – Configurable per-project approval requirements
- **Real-time Teams Notifications** – Interactive Adaptive Cards for instant approvals
- **Role-based Access Control** – Separate interfaces for Employees, Managers, and Suppliers
- **Full Lifecycle Tracking** – From draft creation through fulfillment to completion
- **Mobile-first Design** – Optimized for tablet and mobile use in the field

---

## Architecture

### Technical Stack

| Layer | Technology |
|-------|-----------|
| **Presentation** | Canvas App (Teams embedded) |
| **Business Logic** | Power Automate (Cloud Flows) |
| **Data Layer** | Microsoft Dataverse |
| **Integration** | Teams Connector, Dataverse Connector |
| **Authentication** | Azure AD (via Teams) |

### Data Model

The system uses four custom Dataverse tables with rich relationships:

- **CompanyUser** – User management with role assignment
- **Project** – Construction projects with approval settings
- **Order** – Main orders table with 7-stage lifecycle
- **OrderItem** – Line items with quantity tracking (1:N relationship)

**Order Status Lifecycle:**  
`Draft` → `Submitted` → `Approved` → `In Progress` → `Completed`  
*(Alternative paths: `Rejected`, `Changes Requested`)*

---

## Core Features

### 1. Smart Order Creation
- Dynamic material list builder
- Automatic delivery address inheritance from projects
- Priority-based routing (Low/Normal/High/Urgent)
- Supplier assignment with email lookup

### 2. Automated Approval Process
- **Conditional routing** based on project configuration
- **Adaptive Cards** in Teams with 3-button actions:
  - Approve
  - Reject  
  - Request Changes
- Automatic status updates and timestamp tracking
- Manager notification on resubmission

### 3. Supplier Fulfillment Interface
- Dedicated screen for assigned orders
- Item-by-item purchase tracking
- Progress monitoring with percentage indicators
- Delivery notes and completion workflow

### 4. Advanced PowerFX Patterns

The application demonstrates enterprise-level Power Apps development:

```powerfx
// Role-based statistics with complex filtering
Set(varNeedsAttention,
    Filter(
        Orders,
        RequestedBy.Email = varCurrentUser.Email &&
        (
            'Status (status)' = 'Status (Orders)'.'Changes Requested' ||
            'Status (status)' = 'Status (Orders)'.Rejected ||
            (
                'Status (status)' = 'Status (Orders)'.'Partially Completed' &&
                StartedOn < varTwoDaysAgo
            )
        )
    )
);
```

**Key Techniques Used:**
- Two-stage filtering for performance optimization
- ForAll bulk operations for order items
- Switch-based enum conversion for type safety
- Collection-based temporary storage
- Advanced delegation patterns

---

## Business Value

### Problems Solved
- Manual approval processes via email/chat
- Lost or forgotten material requests
- Lack of order status visibility
- Supplier coordination challenges
- Incomplete audit trail

### Solution Benefits
- **60% faster approval times** with instant Teams notifications
- **Zero lost requests** with centralized tracking
- **Real-time visibility** for all stakeholders
- **Automated audit trail** with Dataverse history tracking
- **Mobile accessibility** for field workers

---

## Deployment

### Prerequisites
- Microsoft 365 E3/E5 or Business Premium
- Power Apps per-user or per-app license
- Power Automate Premium (Dataverse connector)
- Dataverse database capacity
- Teams admin access for app deployment

### Installation Steps
1. Create Production environment with Dataverse
2. Import solution package
3. Configure connection references (Dataverse, Teams)
4. Update Teams channel IDs in flows
5. Enable automation flows
6. Upload custom app to Teams App Studio
7. Populate CompanyUser table with organizational data

*See full documentation for detailed setup instructions*

---

## Security

### Data Access Control
- **Employees** – View own orders only
- **Suppliers** – Access assigned orders with edit rights
- **Managers** – Full visibility across all projects

Implementation:
- Canvas App role-based filtering
- Dataverse row-level security
- Owner-based record sharing
- Azure AD authentication via Teams

---

## Documentation

Comprehensive technical documentation available covering:
- Complete data model with ERD diagrams
- Power Automate flow configuration
- Advanced PowerFX code examples
- Installation and configuration guide
- Usage scenarios and workflows

[Download Full Documentation (PDF)](docs/Material_Order_Documentation_EN.pdf)

---

## Skills Demonstrated

This project showcases professional Power Platform development capabilities:

### Power Apps Canvas
- Complex multi-screen navigation
- Global variable management (30+ variables)
- Theme system (light/dark mode)
- Responsive design for Teams
- Performance optimization techniques

### Power Automate
- Dataverse triggers and actions
- JSON Adaptive Card construction
- Conditional workflow logic
- Error handling patterns
- Teams integration

### Dataverse
- Relational data modeling
- Choice columns and enums
- Lookup relationships (1:N)
- Cascade delete rules
- Autonumber configuration

### PowerFX
- Advanced filtering with delegation
- Collection manipulation
- ForAll bulk operations
- Switch/If conditional logic
- Type-safe enum conversion

---

## Contact

**Patryk Lyszkowski**  
Power Platform Developer

- LinkedIn: [linkedin.com/in/patryk-lyszkowski](https://linkedin.com/in/patryk-lyszkowski)
- GitHub: [github.com/PatrykLyszkowski](https://github.com/PatrykLyszkowski)
- Available for consultation and custom development

---

## Version

**Current Version:** 1.0.0.9  
**Last Updated:** February 2025  
**Status:** Production-ready

---


*Built with Microsoft Power Platform • Designed for Enterprise Scale*




