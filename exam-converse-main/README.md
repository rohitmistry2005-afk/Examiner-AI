# Exam Converse

MASTER PROMPT — EXAMINERAI COMPLETE FRONTEND

You are an expert product designer, UX architect, and senior frontend engineer tasked with building the complete ExaminerAI frontend.

The supplied visual references are the PRIMARY visual source of truth for the appearance of each designed screen.

The product requirements below are the SECONDARY source of truth for semantics, functionality, navigation, interaction, and application behavior.

1. PRODUCT IDENTITY

Product Name

ExaminerAI

Product Category

AI-powered conversational technical examination simulator for college/university students.

Core Product Concept

ExaminerAI is an AI examiner, not a conventional examination website and not a chatbot added somewhere inside an examination platform.

The entire examination experience must be conducted conversationally through the AI examiner.

The student does not navigate through a traditional list of static questions.

Instead:

The AI examiner conducts the examination.

The AI:

asks the examination question

waits for the student's natural response

understands and evaluates the response

determines whether the student actually understands the concept

identifies missing concepts and misconceptions

asks targeted follow-up questions when necessary

dynamically adapts difficulty

targets weak topics

continues the examination conversationally

determines when the examination is complete

generates the final performance report

The primary product experience is therefore:

STUDENT ↔ AI EXAMINER

The interface must visually communicate an actual examiner-student conversation.

2. CORE EXAMINATION LOOP

The complete examination loop is:

CONFIGURE
→ CREATE EXAM SESSION
→ AI EXAMINER INTRODUCTION
→ AI ASKS QUESTION
→ STUDENT RESPONDS
→ AI ANALYZES RESPONSE
→ AI EVALUATES UNDERSTANDING
→ AI PROVIDES APPROPRIATE RESPONSE
→ FOLLOW-UP IF REQUIRED
→ ADAPT DIFFICULTY / TOPIC
→ AI ASKS NEXT QUESTION
→ CONTINUE CONVERSATION
→ EXAM COMPLETED
→ FINAL AI PERFORMANCE REPORT

The conversational loop is the heart of the product.

Do NOT turn this into:

Question List
→ Answer Form
→ Submit
→ Next Question

That would contradict the core product concept.

3. PRODUCT EXPERIENCE PRINCIPLE

The product should feel like:

"I am sitting in front of an intelligent examiner."

It should NOT feel like:

a conventional LMS

a static question bank

a quiz application

an MCQ platform

a generic chatbot

a messaging application

a generic AI assistant

a generic SaaS dashboard

a gamified learning platform

The AI examiner should feel:

intelligent

authoritative

academically credible

calm

conversational

adaptive

precise

professional

focused

The experience should combine:

Academic examination
+
Conversational AI
+
Premium product design

4. REQUIRED FRONTEND PAGES

Implement exactly these primary application pages:

Homepage

Login

Signup

Exam Configuration

AI Examiner Chat Interface

Final Performance Report

Exam History / Progress

Do NOT create a separate Dashboard page.

The AI Examiner Chat Interface is the central authenticated product experience.

5. ROUTING STRUCTURE

Use a clean route architecture:

/

/login

/signup

/exam/configure

/exam/:sessionId

/exam/:sessionId/report

/history

Routes must be reusable and prepared for backend integration.

Authentication-protected pages:

Exam Configuration

AI Examiner

Final Report

History / Progress

Unauthenticated users can access:

Homepage

Login

Signup

6. GLOBAL DESIGN LANGUAGE

Preserve the established ExaminerAI visual identity.

Design personality:

Minimal

Premium

Intelligent

Calm

Precise

Editorial

Academic

Technically sophisticated

Visual principle:

"Less interface, more focus."

Premium quality should come from:

typography

spacing

proportion

hierarchy

controlled contrast

subtle depth

restrained color

excellent component composition

Do not create visual complexity by adding unnecessary components.

7. COLOR SYSTEM

Use these canonical visual tokens.

PRIMARY DARK:

#071021

DARK INK:

#0B1327

NAVY:

#111C35

DEEP BLUE:

#17264A

PRIMARY INDIGO:

#5865F2

BRIGHT INDIGO:

#6873FF

SECONDARY VIOLET:

#8B7CFF

WHITE:

#FFFFFF

PAGE BACKGROUND:

#F7F9FC

SECONDARY SURFACE:

#F1F4F9

LIGHT SURFACE:

#E9EEF6

PRIMARY TEXT:

#102348

SECONDARY TEXT:

#465675

MUTED TEXT:

#6F7D98

BORDER:

#E1E7F0

SUCCESS:

#16A34A

WARNING:

#D97706

ERROR:

#DC2626

Color meaning:

Navy / dark:
brand foundation, authority, examiner environment

Indigo:
AI presence, active states, primary actions, progress, emphasis

Green:
correct/strong state

Amber:
attention/moderate understanding

Red:
incorrect/critical knowledge gap

IMPORTANT:

Indigo must remain controlled.

Do not make the entire application blue or purple.

8. TYPOGRAPHY

Use two complementary font families.

DISPLAY FONT:

Instrument Serif

Fallback:

Georgia, Times New Roman, serif

UI FONT:

Inter

Fallback:

system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif

Display typography:

major headings

homepage hero

report headline

important metrics

major empty states

Inter:

navigation

body

buttons

chat messages

exam controls

metadata

cards

forms

application interface

The visual language should maintain:

EDITORIAL + TECHNICAL

contrast.

9. SPACING SYSTEM

Use an 8px-based spacing system.

Core values:

4
8
12
16
20
24
32
40
48
56
64
80
96
120

Semantic tokens:

--space-xs: 4px
--space-sm: 8px
--space-md: 16px
--space-lg: 24px
--space-xl: 32px
--space-2xl: 48px
--space-3xl: 64px
--space-4xl: 80px
--space-5xl: 96px

Maintain generous whitespace.

Do not compress interfaces unnecessarily.

10. CONTAINER AND GRID

Desktop maximum content width:

1200px

Desktop horizontal padding:

40–48px

Mobile:

20–24px

Use a responsive 12-column grid for marketing pages.

Application pages may use specialized workspace layouts where necessary.

Never allow horizontal overflow.

11. BORDER RADIUS

Use:

8px
10px
12px
16px
20px
999px

Usage:

Inputs:
12px

Buttons:
10–12px

Cards:
16px

Chat message surfaces:
14–18px

Application panels:
16–20px

Badges:
999px

Do not make every element pill-shaped.

12. SHADOW SYSTEM

Use subtle ambient elevation.

Shadow XS:

0 2px 8px rgba(16,35,72,0.04)

Shadow SM:

0 6px 18px rgba(16,35,72,0.05)

Shadow MD:

0 12px 32px rgba(16,35,72,0.08)

Shadow LG:

0 24px 60px rgba(8,18,39,0.18)

Accent Glow:

0 0 40px rgba(88,101,242,0.18)

Avoid dramatic shadows.

13. GLOBAL COMPONENT SYSTEM

Build reusable components.

Create:

Navbar

Logo

Button

SecondaryButton

IconButton

Badge

Card

SectionHeader

Divider

Input

Textarea

Select

Modal

Toast

StatusIndicator

ProgressIndicator

Avatar

ChatMessage

ChatComposer

AIIndicator

ExamProgress

ReportCard

Metric

EmptyState

LoadingState

Do not duplicate styling unnecessarily.

Use centralized design tokens.

14. HOMEPAGE

The homepage remains a premium marketing experience.

Structure:

NAVBAR
→ HERO
→ TRUST METRICS
→ FEATURES
→ HOW IT WORKS
→ FINAL CTA
→ FOOTER

No dashboard.

No additional homepage sections.

15. HOMEPAGE HERO

Primary message:

"Practice like you’re facing a real examiner."

Emphasize:

"real examiner"

with controlled indigo.

Supporting concept:

ExaminerAI evaluates how you think, detects what you don't understand, and adapts the examination around your performance.

Primary CTA:

START AN EXAMINATION →

Secondary CTA:

SEE HOW IT WORKS

16. HOMEPAGE PRODUCT VISUAL

The hero product visualization must now communicate the NEW product concept.

IMPORTANT:

Do NOT present the product as a conventional question-and-answer examination dashboard.

The mockup must visually show:

AI Examiner ↔ Student conversation

The mockup may contain:

AI Examiner message:

"Let's begin with a question about binary search trees. Can you explain how the search operation works and why its average complexity is O(log n)?"

Student response:

"In a balanced tree, we eliminate roughly half of the remaining nodes at each step..."

AI evaluation state:

"Analyzing understanding..."

Then:

"Your explanation is mostly correct. Let's go one step deeper."

Follow-up question:

"What changes when the tree becomes highly unbalanced?"

This is a marketing representation of the real conversational examination experience.

The visual should make the concept immediately obvious.

17. LOGIN PAGE

Create a clean premium authentication screen.

Layout:

Centered authentication card or refined split-screen composition.

Include:

ExaminerAI logo

Welcome heading

Email

Password

Remember me

Sign In

Forgot password

Continue with supported authentication options if implemented

Link to Signup

Maintain the ExaminerAI visual language.

Do not turn authentication into a generic template.

18. SIGNUP PAGE

Create:

ExaminerAI logo

Create account heading

Name

Email

Password

Confirm password

Create Account

Existing account → Sign In

Keep the experience minimal and focused.

19. EXAM CONFIGURATION PAGE

This is the only setup page required before entering the examiner.

The student configures:

Subject

Syllabus / Topics

Exam Mode

Difficulty

Number of Questions

Exam modes may include:

Semester Exam

Viva

Technical Test

Subject-specific Assessment

The configuration page should feel like:

Preparing to enter an examination

not like configuring a generic quiz.

Use a focused, premium layout.

Provide a clear primary action:

START EXAMINATION →

On submission:

Create the exam session and navigate directly into the AI Examiner Chat Interface.

Do not navigate to a Dashboard.

20. AI EXAMINER CHAT INTERFACE

This is the MOST IMPORTANT PAGE in the entire product.

The examination must happen here.

The page should feel like a real-time conversation between:

Student

and

AI Examiner

21. AI EXAMINER INTERFACE STRUCTURE

Recommended desktop structure:

LEFT / PRIMARY:

Conversation workspace

RIGHT / SECONDARY:

Compact examination context panel

The conversation must remain visually dominant.

Do not make the right panel more important than the conversation.

Possible structure:

┌───────────────────────────────────────────────┐
│ ExaminerAI Data Structures Q4 / 10 │
├───────────────────────────────────────────────┤
│ │
│ AI EXAMINER │
│ ┌───────────────────────────────────────────┐ │
│ │ Explain how a binary search tree works. │ │
│ └───────────────────────────────────────────┘ │
│ │
│ STUDENT │
│ ┌───────────────────────────────────────────┐ │
│ │ A BST organizes nodes so that... │ │
│ └───────────────────────────────────────────┘ │
│ │
│ AI EXAMINER │
│ ┌───────────────────────────────────────────┐ │
│ │ Good. Now let's examine your reasoning │ │
│ │ a little further... │ │
│ └───────────────────────────────────────────┘ │
│ │
│ ┌───────────────────────────────────────────┐ │
│ │ Type your answer... │ │
│ └───────────────────────────────────────────┘ │
│ [Send →] │
└───────────────────────────────────────────────┘

22. EXAMINER HEADER

Header should contain:

ExaminerAI logo

Subject

Exam mode

Question progress

Optional timer

Exit / pause control

Example:

ExaminerAI
Data Structures
Technical Examination
Question 4 of 10
24:30

Keep the header compact.

23. AI EXAMINER IDENTITY

The AI examiner must have a clearly recognizable identity.

Use:

subtle AI mark

small avatar/abstract examiner symbol

"AI Examiner" label

Do NOT use:

robot head

cartoon character

generic ChatGPT-style icon

childish avatar

The examiner should feel professional and academic.

24. CONVERSATIONAL MESSAGE SYSTEM

AI messages and student messages must be visually distinguishable.

AI messages:

refined light surface

subtle border

restrained indigo identity

clear examiner label

Student messages:

slightly different surface

clear student identity

readable typography

Avoid making the interface look like WhatsApp, Discord, or a generic messaging application.

It is an examination conversation, not casual chat.

25. AI EXAMINER BEHAVIOR STATES

Design the interface to support these states:

Examiner introduction

Asking question

Waiting for answer

Student responding

AI analyzing

AI evaluating

Feedback

Follow-up question

Difficulty adaptation

Next question

Examination completion

AI analyzing state:

Show a subtle processing indicator.

Example:

Analyzing your response...

Possible internal indicators:

Understanding key concepts

Checking correctness

Assessing reasoning

Identifying gaps

These indicators should remain subtle.

Do not expose unnecessary technical implementation details.

26. FOLLOW-UP / SOCRATIC QUESTIONING

This is a defining ExaminerAI feature.

When the student's response is:

incomplete

ambiguous

partially correct

conceptually weak

based on a misconception

the AI examiner should continue the conversation.

Example:

Student:

"I think the algorithm is O(log n) because it searches the tree."

AI Examiner:

"You're on the right track. But the complexity depends on the structure of the tree. What happens when the tree becomes completely unbalanced?"

The UI should make this feel like a natural examiner conversation.

Do NOT show it as:

"Question 4B"

or

"Follow-up form."

It is part of the same conversation.

27. ADAPTIVE EXAMINATION

The interface should support the AI silently adapting:

Strong performance:
→ harder question

Average performance:
→ similar difficulty

Weak performance:
→ easier/reinforcement question

Weak topic:
→ targeted question

The student should experience this as natural examiner behavior.

Do not expose technical algorithmic decision logic unnecessarily.

28. ANSWER COMPOSER

The answer area is conversational.

Use:

large textarea

placeholder such as "Explain your reasoning..."

send button

optional keyboard shortcut

character count only if useful

Do NOT make it look like an ordinary form submission.

The student should feel like they are responding directly to the examiner.

Primary action:

SEND ANSWER →

After submission:

Disable duplicate submission while processing.

Show AI analysis state.

29. EXAM PROGRESS

Show examination progress without making it gamified.

Example:

Question 4 of 10

Use subtle progress indicators.

Avoid:

XP

points animations

badges

streaks

celebratory effects

game-like progress bars

This is an academic examination.

30. EXAMINATION COMPLETION

When the AI determines the examination is complete, the conversation should transition naturally.

Example:

AI Examiner:

"That concludes your examination. I've analyzed your responses and prepared your performance assessment."

Then provide:

VIEW PERFORMANCE REPORT →

The transition should feel calm and professional.

31. FINAL PERFORMANCE REPORT

The report is the second most important application page after the AI Examiner.

It summarizes the complete conversational examination.

The report should contain:

Overall Performance

Overall Score

Accuracy

Average Score

Topic-wise Performance

Strong Topics

Weak Topics

Missing Concepts

Difficulty Progression

Examiner Feedback

Concepts to Revise

Personalized Recommendations

The final report must communicate:

What the student actually understands.

Not simply:

How many questions were correct.

32. REPORT STRUCTURE

Recommended structure:

Header:

"Your Examination Report"

Summary:

Overall Performance

Score

Accuracy

Average Score

Then:

Strong Areas

Weak Areas

Knowledge Gaps

Difficulty Progression

AI Examiner Feedback

Recommended Revision

Primary action:

START ANOTHER EXAMINATION →

Secondary:

VIEW EXAM HISTORY

Use charts only where they improve comprehension.

Avoid dashboard-style information overload.

33. KNOWLEDGE GAP VISUALIZATION

Represent:

Strong Topics
Moderate Topics
Weak Topics
Missing Concepts

Use restrained visual indicators.

Do not use excessive graphs.

The report should feel like an academic assessment document enhanced by AI.

34. EXAM HISTORY / PROGRESS

The History page replaces the need for a Dashboard.

Show previous examinations.

Each record may include:

Subject

Exam mode

Date

Score

Accuracy

Difficulty

Status

View Report

Provide a clear:

START NEW EXAMINATION →

The page should remain focused.

Do not turn it into a large administrative dashboard.

35. NAVIGATION

Marketing navigation may include:

Home
How It Works
Features
For Educators
Pricing
About

Authenticated application navigation should remain simpler.

Do NOT create a large dashboard sidebar.

The application navigation should prioritize:

New Examination

Examination History

Profile / Account

The AI Examiner remains the primary destination.

36. RESPONSIVE SYSTEM

Breakpoints:

640px
768px
1024px
1280px
1440px

Desktop:

spacious examination workspace

conversation dominant

compact contextual information

Tablet:

reduce secondary context

preserve conversation readability

Mobile:

single-column conversation

compact header

full-width message area

full-width composer

secondary exam context accessible through a compact control if necessary

The conversation must remain the primary interface.

Never squeeze two complex panels side-by-side on small screens.

37. MOBILE AI EXAMINER

Mobile should feel like a focused examination conversation.

Structure:

Header

↓

Question progress

↓

AI message

↓

Student response

↓

AI evaluation/follow-up

↓

Answer composer

Do not allow the interface to become a generic messaging app.

38. INTERACTION SYSTEM

Motion must be subtle and purposeful.

Timing:

100ms instant
150ms fast
200ms standard
300ms slow
450ms emphasis

Primary easing:

cubic-bezier(0.22, 1, 0.36, 1)

Buttons:

hover translateY(-1px)

active scale(.985)

subtle shadow/brightness change

Chat messages:

subtle appearance transition

AI processing:

restrained shimmer/pulse

Avoid:

excessive parallax

spinning elements

aggressive bounce

constant animated gradients

particles

gamification

39. ACCESSIBILITY

Requirements:

semantic HTML

correct heading hierarchy

strong contrast

keyboard navigation

visible focus states

accessible buttons

accessible forms

accessible chat composer

meaningful labels

meaningful alt text

reduced-motion support

Focus:

2px indigo outline
3px offset

Respect:

prefers-reduced-motion

Do not communicate important information only through color.

40. DESIGN TOKENS

Create centralized tokens.

Typography:

--font-display
--font-sans

Colors:

--color-ink-950
--color-ink-900
--color-navy-800
--color-navy-700
--color-indigo-600
--color-indigo-500
--color-violet-500
--color-white
--color-surface-50
--color-surface-100
--color-surface-200
--color-text-950
--color-text-700
--color-text-500
--color-border
--color-success
--color-warning
--color-error

Spacing:

--space-xs
--space-sm
--space-md
--space-lg
--space-xl
--space-2xl
--space-3xl
--space-4xl
--space-5xl

Radius:

--radius-sm
--radius-md
--radius-lg
--radius-xl
--radius-2xl
--radius-pill

Shadows:

--shadow-xs
--shadow-sm
--shadow-md
--shadow-lg
--shadow-glow

Motion:

--duration-fast
--duration
--duration-slow
--ease

41. COMPONENT ARCHITECTURE

Use reusable components.

Recommended structure:

ExaminerAI
│
├── Marketing
│ ├── Navbar
│ ├── Homepage
│ │ ├── Hero
│ │ ├── TrustMetrics
│ │ ├── FeatureSection
│ │ ├── HowItWorks
│ │ ├── CTASection
│ │ └── Footer
│
├── Authentication
│ ├── Login
│ └── Signup
│
├── Examination
│ ├── ExamConfiguration
│ ├── AIExaminer
│ │ ├── ExaminerHeader
│ │ ├── Conversation
│ │ ├── ChatMessage
│ │ ├── AIProcessingState
│ │ ├── FollowUpMessage
│ │ ├── ExamProgress
│ │ └── AnswerComposer
│ │
│ └── PerformanceReport
│
└── History
├── ExamHistory
└── ExamHistoryItem

42. FRONTEND/BACKEND SEPARATION

The frontend must be prepared for real backend integration.

Do not hardcode AI responses as the actual architecture.

The UI should be capable of consuming:

Exam Session
Question
Student Response
Evaluation
Follow-up Question
Difficulty
Topic
Performance
Final Report

The backend will eventually provide these through APIs.

The frontend should provide clear loading, error, empty, and success states.

43. DATA FLOW EXPECTATION

The frontend should support this conceptual flow:

Student
↓
Exam Configuration
↓
Create Exam Session
↓
AI Examiner
↓
AI Question
↓
Student Response
↓
Backend Evaluation
↓
AI Feedback / Follow-up
↓
Next Question
↓
Repeat
↓
Exam Completed
↓
Final Report
↓
History

The frontend must not assume that every question is independent.

The conversation represents one continuous examination session.

44. IMPORTANT EXAMINATION UX RULE

Never design the AI Examiner as a normal examination form with a chatbot attached to it.

The AI conversation itself IS the examination.

The examiner asks.

The student answers.

The examiner evaluates.

The examiner probes deeper.

The examiner adapts.

The examiner continues.

The examiner concludes.

This principle overrides conventional examination UI patterns.

45. WHAT MUST NOT BE IMPLEMENTED

Do NOT introduce:

Dashboard

Static question bank

MCQ-first interface

Quiz-game mechanics

XP

streaks

leaderboards

unnecessary gamification

generic chatbot sidebar

generic AI assistant layout

unnecessary admin panels

unrelated SaaS features

excessive charts

excessive cards

unnecessary badges

robot illustrations

cyberpunk/neon AI styling

excessive gradients

excessive glassmorphism

particle backgrounds

complex animations

46. VISUAL QUALITY BAR

The final product must look professionally designed.

Avoid:

generic Tailwind defaults

inconsistent spacing

inconsistent radii

excessive borders

poor typography

oversized buttons

cramped layouts

random gradients

excessive cards

arbitrary colors

poor iconography

placeholder imagery

low-quality mockups

horizontal overflow

unnecessary UI elements

Every element must have a purpose.

47. MOST IMPORTANT VISUAL ANCHORS

Preserve these throughout the product:

Dark cinematic homepage hero

Editorial serif typography

Controlled indigo accent

Premium ExaminerAI branding

Strong whitespace

Academic credibility

Conversational AI examiner experience

AI examiner identity

Natural student/examiner message exchange

Subtle AI evaluation state

Conversational follow-up questioning

Adaptive examination behavior

Clear examination progress

High-quality final performance report

Consistent visual system across all pages

48. PAGE RELATIONSHIP

The product should feel like one continuous experience:

HOMEPAGE
↓
SIGN UP / LOGIN
↓
EXAM CONFIGURATION
↓
AI EXAMINER
↓
FINAL PERFORMANCE REPORT
↓
EXAM HISTORY

Do not insert a Dashboard between these stages.

The AI Examiner is the central product.

49. IMPLEMENTATION PRIORITY

PHASE 1:

Global design tokens
Typography
Responsive container
Core components
Routing
Navbar

PHASE 2:

Homepage

PHASE 3:

Authentication

Login
Signup

PHASE 4:

Exam Configuration

PHASE 5:

AI Examiner Chat Interface

This phase receives the highest UX priority.

Implement:

conversation

AI states

student responses

follow-ups

progress

adaptive-state representation

completion

PHASE 6:

Final Performance Report

PHASE 7:

Exam History / Progress

PHASE 8:

Responsive refinement
Accessibility
Interaction polish
Loading states
Error states
Performance optimization

50. FINAL INSTRUCTION TO THE AI CODING PLATFORM

Build ExaminerAI as a conversational AI examiner, not as a conventional examination website.

The homepage should market the concept.

The authenticated product should deliver the concept.

The most important screen is the:

AI EXAMINER CHAT INTERFACE

The examination itself must occur conversationally.

The student should feel that they are being examined by an intelligent examiner rather than filling out an online test.

The examiner should:

GENERATE
→ ASK
→ LISTEN
→ EVALUATE
→ DIAGNOSE
→ PROBE
→ ADAPT
→ CONTINUE
→ CONCLUDE

The visual design should communicate intelligence through restraint, typography, spacing, hierarchy, and interaction quality.

Do not turn ExaminerAI into a generic chatbot.

Do not turn ExaminerAI into a quiz platform.

Do not turn ExaminerAI into an LMS.

Do not create a Dashboard.

Do not create a static question-list workflow.

Do not place a chatbot "somewhere inside" the examination website.

Instead:

THE CHAT IS THE EXAMINATION.

The final product should feel:

Premium
+
Academic
+
Conversational
+
Intelligent
+
Adaptive
+
Focused

The strongest product identity should come from:

DARK NAVY
+
WARM WHITE
+
CONTROLLED INDIGO
+
EDITORIAL SERIF
+
INTER UI
+
GENEROUS WHITESPACE
+
SUBTLE DEPTH
+
CONVERSATIONAL AI EXAMINER

Most importantly, a user should understand within seconds that:

ExaminerAI does not simply give students questions.

It conducts an intelligent examination conversation that continuously evaluates, diagnoses, adapts, and challenges the student's actual understanding.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/b7c93e84-592e-44ca-9279-4344bf0742de).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
