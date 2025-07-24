report_text = """Exploratory Testing Report
Project: Hochschule Bremen Website
Session Duration: 1 hour
Execution Date: May 16, 2025
Testing Team: Laura Meier, Jonas Schmidt, Aisha Khalid

---
1. Objectives and Scope
- Primary objective: Evaluate the usability, stability, and basic functionality of the Hochschule Bremen institutional website through exploratory testing.
- Areas reviewed:
  - Home page
  - "Study Programs" section
  - Internal search
  - Contact and information request forms
  - Content accessibility (menus, links, buttons)

---
2. Test Environment
- Device / OS:
  - Dell laptop, Windows 10
  - MacBook Pro, macOS 13 Ventura
  - Samsung Galaxy S22 smartphone, Android 13
- Browsers:
  - Chrome 113.0
  - Firefox 117.0
  - Safari 16.4
- Network connection: Fiber optic, 100 Mbps

---
3. Methodology
1. Free exploration session to get familiar with navigation.
2. Guided tasks simulating prospective student actions:
   - Search for master’s programs in engineering.
   - Fill out the information request form.
3. Real-time logging of findings, classifying defects by severity.
4. Screenshot capture of unexpected behaviors.

---
4. Key Findings
ID   | Component                      | Issue Description                                                                      | Severity  | Recommendation
-----|--------------------------------|----------------------------------------------------------------------------------------|-----------|-------------------------------------------------------
D-001| Main menu (desktop)            | "Programs" submenu flickers when quickly hovering, making option selection difficult.   | Medium    | Adjust hover delay or implement debounce.
D-002| Internal search                | Searching “Engineering” takes >5 s to return results, and loading bar stalls at 90 %.    | High      | Optimize search API; review queries and implement pagination.
D-003| Contact form                   | After submission, page reloads without confirmation message, leaving user unsure.      | Critical  | Add “Thank you for your request” message or redirect to confirmation page.
D-004| Mobile: “News” section         | On Android/Chrome, images overlap titles when rotating from portrait to landscape.      | Medium    | Review responsive CSS; use flex-wrap or media queries to adjust layout.
D-005| External links                 | Library portal link opens in the same tab, interrupting the session.                   | Low       | Set external links to open with target="_blank" and rel="noopener noreferrer".
D-006| Color contrast                 | Secondary text in “Events” section (light gray on white) fails WCAG AA contrast ratio. | Medium    | Adjust text or background color to achieve minimum 4.5:1 contrast.

---
5. Additional Observations
- Usability:
  - Navigation is intuitive with a well-organized menu.
  - Breadcrumbs are missing in inner sections to facilitate quick return.
- Performance:
  - Home page load time: ~2 s.
  - Flash of unstyled text due to slow-loading web fonts.
- Accessibility:
  - Some form buttons lack aria-label attributes.
  - Recommend running an accessibility scan with Axe or WAVE.

---
6. Conclusions and Recommendations
1. Urgently fix the contact form behavior (D-003) and optimize search (D-002).
2. Improve mobile usability in the News section.
3. Enhance accessibility: adjust contrast and add ARIA labels.
4. Implement monitoring tools to track performance and detect regressions.

---
Next Steps:
- Prioritize critical and high-severity defects in the next development iteration.
- Schedule a second testing session after fixes.
- Integrate end-to-end automated tests for key workflows.

---
End of Report
"""

test_plan = """{
  "objective": "To evaluate the usability and findability of information in the study program overview section for prospective students on the Hochschule Bremen web portal.",
  "steps": [
    {
      "step_number": 1,
      "action": "Access the web portal of Hochschule Bremen on both mobile and desktop devices.",
      "expected_outcome": "The homepage should load successfully without errors on both platforms.",
      "notes": "Ensure internet connectivity and device compatibility."
    },
    {
      "step_number": 2,
      "action": "Navigate to the 'Study Program Overview' section from the homepage.",
      "expected_outcome": "User should be able to locate and access the study program section with ease.",
      "notes": "Assess the visibility and accessibility of the navigation menu."
    },
    {
      "step_number": 3,
      "action": "Examine the layout and organization of information within the study program section.",
      "expected_outcome": "Information should be clearly presented and easy to comprehend.",
      "notes": "Look for logical categorization and intuitive design."
    },
    {
      "step_number": 4,
      "action": "Simulate a user task to find a specific study program or course details.",
      "expected_outcome": "User should be able to locate detailed information quickly and efficiently.",
      "notes": "Evaluate search functionality and filtering options, if available."
    },
    {
      "step_number": 5,
      "action": "Check the responsiveness and navigation smoothness on different screen sizes (mobile vs. desktop).",
      "expected_outcome": "The site should adjust seamlessly between different screen sizes, maintaining usability.",
      "notes": "Observe any layout shifts or navigation issues."
    },
    {
      "step_number": 6,
      "action": "Test for any accessibility features, such as screen reader compatibility or keyboard navigation.",
      "expected_outcome": "The site should be accessible to users with disabilities, complying with basic accessibility standards.",
      "notes": "Use tools like a screen reader to verify accessibility support."
    },
    {
      "step_number": 7,
      "action": "Review the loading speed of the study program overview page.",
      "expected_outcome": "The page should load quickly without noticeable delays.",
      "notes": "Use tools like Google PageSpeed Insights for objective measurement."
    },
    {
      "step_number": 8,
      "action": "Test interactive elements like links and buttons in the study programs section.",
      "expected_outcome": "All links and buttons should function as expected and guide users correctly.",
      "notes": "Check for broken links or incorrect redirects."
    },
    {
      "step_number": 9,
      "action": "Evaluate the visual consistency of the study programs section with the rest of the site.",
      "expected_outcome": "The visual design should be consistent and provide a cohesive experience.",
      "notes": "Look for consistent fonts, colors, and layouts."
    },
    {
      "step_number": 10,
      "action": "Attempt to access the study program overview section from different entry points within the website.",
      "expected_outcome": "Multiple pathways should exist to access the study programs, enhancing user navigation.",
      "notes": "Identify if secondary paths (e.g., footer, sidebar) are available and usable."
    },
    {
      "step_number": 11,
      "action": "Test the site's behavior under different network conditions using tools like throttling in browsers.",
      "expected_outcome": "The site should remain usable even under slow network conditions.",
      "notes": "Observe any significant degradation in user experience."
    },
    {
      "step_number": 12,
      "action": "Check if the search feature can recognize typo errors and offer suggestions.",
      "expected_outcome": "The search should be robust enough to handle user mistakes and provide relevant suggestions.",
      "notes": "Test with common typographical errors."
    },
    {
      "step_number": 13,
      "action": "Assess user feedback mechanisms such as contact forms or chat support in the study programs section.",
      "expected_outcome": "There should be clear and accessible ways to contact support for further inquiries.",
      "notes": "Test functionality and response time of feedback mechanisms."
    },
    {
      "step_number": 14,
      "action": "Explore the use of multimedia elements (if any) in the study programs section for enhancing understanding.",
      "expected_outcome": "Multimedia elements like videos or images should load correctly and enhance user understanding.",
      "notes": "Ensure accessibility features like captions or alt texts are present."
    },
    {
      "step_number": 15,
      "action": "Test session management by keeping the session active across different pages and revisiting the study programs section.",
      "expected_outcome": "User session should remain active, and previous actions retained as expected.",
      "notes": "This checks for login states and personalization continuity."
    },
    {
      "step_number": 16,
      "action": "Examine the use of language and terminology for clarity and relevance to prospective students.",
      "expected_outcome": "Language should be simple, clear, and relevant to the target audience.",
      "notes": "Identify any jargon or complex terms that might confuse users."
    }
  ],
  "additional_notes": "Focus on identifying any barriers to user satisfaction, and document any observed usability issues or suggestions for improvement."
}"""

# Info for the project
project_name = "Website Test HSB"
project_description = "Exploring usability & navigation for the target group prospective students."

# Info for the test session (in theory we can change this later on)

testsession_name= "Exploratory Testing Session - Hochschule Bremen Website"
test_object = "Web portal Hochschule Bremen"
test_objective = "Usability & information findability for prospective students"
introduction_object =("This test plan outlines the exploratory testing approach for evaluating the usability and "
                      "information findability of the Hochschule Bremen web portal, specifically focusing on the "
                      "study program overview section. The goal is to ensure that prospective students can easily navigate and access relevant information on both mobile and desktop devices.")
focus_test = "Study program overview section, navigation, information clarity"

