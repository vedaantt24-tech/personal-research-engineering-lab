Database model plan: User, Profile, Education, Skill, Interest, Experience, Project, ProjectTechnology, Research, ResearchReference, Idea, IdeaVersion, Experiment, Publication, BlogPost, Media, Tag, ContactMessage, CollaborationRequest, AgreementTemplate, AgreementAcceptance, PermissionGrant, AccessEvent, AuditLog, SocialLink, Resume, VisibilitySetting, AnalyticsEvent.

AgreementAcceptance must preserve the exact accepted agreement version and SHA-256 hash. AccessEvent records protected-content access. Single-owner authorization is mandatory; public visitors have no account.
