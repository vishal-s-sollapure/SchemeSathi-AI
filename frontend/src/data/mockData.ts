import { Scheme, Scholarship, Citation, DocumentAnalysisResult } from '../types';

export const DEMO_DATA_DISCLAIMER = "DEMO DATA: The schemes, values, and guidelines shown here are illustrative sample data created for evaluating the SchemeSathi AI interface. They do not constitute official legal or government verification.";

export const MOCK_SCHEMES: Scheme[] = [
  {
    id: 'demo-pm-kisan-2024',
    title: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
    ministry: 'Ministry of Agriculture & Farmers Welfare, Govt of India',
    level: 'Central',
    category: 'Agriculture & Farming',
    annualBenefit: '₹6,000 / year (in 3 equal installments of ₹2,000)',
    benefitType: 'Direct Benefit Transfer (DBT)',
    description: 'Income support to all landholding farmer families across India, having cultivable land in their names, subject to certain exclusion criteria.',
    targetBeneficiaries: 'Small and marginal landholder farmer families',
    eligibilityCriteria: [
      'Landholding farmer families with cultivable land record',
      'Valid Aadhaar linked to primary bank account',
      'No institutional landholders or income tax payers in family'
    ],
    requiredDocuments: [
      'Aadhaar Card with mobile linking',
      'Land Ownership Record (Khatauni / RTC Extract)',
      'Active DBT-enabled Bank Passbook',
      'Self-Declaration Form'
    ],
    officialPortal: 'https://pmkisan.gov.in',
    applicationDeadline: 'Continuous Enrollment (Year-round)',
    isDemo: true,
    demoNote: 'Sample Civic Record for Interface Preview'
  },
  {
    id: 'demo-ayushman-bharat-2024',
    title: 'Ayushman Bharat PM-JAY (Pradhan Mantri Jan Arogya Yojana)',
    ministry: 'National Health Authority (NHA) & Ministry of Health & Family Welfare',
    level: 'Central',
    category: 'Healthcare & Ayushman',
    annualBenefit: 'Cashless health cover up to ₹5,00,000 per family/year',
    benefitType: 'Health Insurance Cover',
    description: 'The world\'s largest government-funded healthcare assurance scheme providing cashless secondary and tertiary hospitalization cover.',
    targetBeneficiaries: 'Bottom 40% vulnerable citizen households based on SECC 2011 criteria',
    eligibilityCriteria: [
      'Listed under Socio-Economic Caste Census (SECC 2011) database',
      'Rural households with kutcha walls/roofs or landless laborers',
      'Identified occupational categories of urban workers'
    ],
    requiredDocuments: [
      'Aadhaar Card or Voter ID Card',
      'Ration Card / Family Identification Certificate',
      'PM-JAY Family ID or Letter from Gram Panchayat'
    ],
    officialPortal: 'https://pmjay.gov.in',
    applicationDeadline: 'Continuous Enrollment',
    isDemo: true,
    demoNote: 'Sample Civic Record for Interface Preview'
  },
  {
    id: 'demo-karnataka-raitha-vidyanidhi',
    title: 'Karnataka Raita Vidya Nidhi Scholarship Program',
    ministry: 'Department of Agriculture, Government of Karnataka',
    level: 'State (Karnataka)',
    category: 'Education & Scholarships',
    annualBenefit: '₹2,500 to ₹11,000 / year based on course level',
    benefitType: 'Direct Benefit Transfer (DBT)',
    description: 'Direct financial assistance for children of verified farmer families in Karnataka pursuing post-matriculation, degree, and professional education.',
    targetBeneficiaries: 'Children of farmers holding verified Karnataka FID in FRUITS portal',
    eligibilityCriteria: [
      'Parent must possess valid Karnataka Farmer Identification (FID)',
      'Student enrolled in recognized post-matric/undergrad/postgrad course',
      'Domicile of Karnataka state'
    ],
    requiredDocuments: [
      'Farmer ID (FRUITS portal FID number)',
      'Student SSP (State Scholarship Portal) ID',
      'Aadhaar of student and farmer parent',
      'Current Year College Bonafide Certificate'
    ],
    officialPortal: 'https://ssp.postmatric.karnataka.gov.in',
    applicationDeadline: '30 November 2026',
    isExpiringSoon: true,
    isDemo: true,
    demoNote: 'Sample Civic Record for Interface Preview'
  },
  {
    id: 'demo-pm-mudra-yojana',
    title: 'Pradhan Mantri MUDRA Yojana (PMMY) — Kishore & Tarun',
    ministry: 'Ministry of Finance & Department of Financial Services',
    level: 'Central',
    category: 'MSME & Entrepreneurship',
    annualBenefit: 'Collateral-free institutional credit up to ₹10,00,000',
    benefitType: 'Credit Support',
    description: 'Refinancing scheme facilitating loans up to 10 Lakhs to non-corporate, non-farm small/micro enterprises with subsidized interest rates.',
    targetBeneficiaries: 'Micro-entrepreneurs, artisans, shopkeepers, and food processing units',
    eligibilityCriteria: [
      'Indian citizen with viable non-farm business plan',
      'No previous default record with any commercial/cooperative bank',
      'Valid Udyam Registration number for the unit'
    ],
    requiredDocuments: [
      'Udyam Registration Certificate',
      'Proof of Identity & Address (Aadhaar/PAN)',
      'Business Project Report / Quotation of Machinery',
      '6 Months Bank Statement'
    ],
    officialPortal: 'https://www.mudra.org.in',
    applicationDeadline: 'Rolling Annual Applications',
    isDemo: true,
    demoNote: 'Sample Civic Record for Interface Preview'
  },
  {
    id: 'demo-pm-awas-gramin',
    title: 'Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)',
    ministry: 'Ministry of Rural Development, Govt of India',
    level: 'Central',
    category: 'Housing & Rural Development',
    annualBenefit: '₹1,20,000 grant (plains) / ₹1,30,000 (hilly/difficult areas) + 90 days MGNREGA wages',
    benefitType: 'Direct Benefit Transfer (DBT)',
    description: 'Providing pucca houses with basic amenities to all houseless households and households living in kutcha and dilapidated houses in rural areas.',
    targetBeneficiaries: 'Houseless families and those living in 0, 1, or 2 room kutcha houses',
    eligibilityCriteria: [
      'Household must be part of permanent PMAY-G priority waitlist',
      'Does not own a pucca house anywhere in India',
      'No family member in regular government employment'
    ],
    requiredDocuments: [
      'Job Card (MGNREGA) number',
      'Aadhaar card of all adult family members',
      'Bank Account passbook linked with Aadhaar/DBT',
      'Gram Sabha Resolution approval certificate'
    ],
    officialPortal: 'https://pmayg.nic.in',
    applicationDeadline: 'Phase 3 Block Allocation Ongoing',
    isDemo: true,
    demoNote: 'Sample Civic Record for Interface Preview'
  },
  {
    id: 'demo-pm-kusum-b',
    title: 'PM-KUSUM Component B: Standalone Solar Agriculture Pumps',
    ministry: 'Ministry of New and Renewable Energy (MNRE)',
    level: 'Central',
    category: 'Agriculture & Farming',
    annualBenefit: 'Up to 60% capital subsidy (30% Central + 30% State Gov)',
    benefitType: 'Subsidy',
    description: 'Support for installation of individual solar-powered agriculture pumps up to 7.5 HP in off-grid rural areas lacking electricity grid connections.',
    targetBeneficiaries: 'Individual farmers, water user associations, and farmer producer groups',
    eligibilityCriteria: [
      'Farmer with cultivable agricultural land and water source',
      'Farmland without existing energized electricity grid pump connection',
      'Consent to bear 40% farmer contribution or bank loan'
    ],
    requiredDocuments: [
      'Record of Rights (RoR) / Land mutation certificate',
      'Electricity DISCOM Non-Availability Certificate (NOC)',
      'Aadhaar and Bank DBT verification letter',
      'Borewell / Open Well inspection report'
    ],
    officialPortal: 'https://pmkusum.mnre.gov.in',
    applicationDeadline: '15 December 2026',
    isExpiringSoon: true,
    isDemo: true,
    demoNote: 'Sample Civic Record for Interface Preview'
  }
];

export const MOCK_SCHOLARSHIPS: Scholarship[] = [
  {
    id: 'demo-post-matric-sc-st',
    title: 'Central Sector Post-Matric Scholarship for SC/ST Students',
    provider: 'Ministry of Social Justice & Empowerment, Govt of India',
    level: 'National / Central',
    targetAudience: 'SC & ST students enrolled in recognized Class 11, 12, Degree, PG, or Professional courses',
    courseLevel: 'Technical / Professional',
    maxAnnualIncome: 250000,
    minPercentage: 50,
    eligibleCategories: ['SC', 'ST'],
    amountPerYear: '₹13,500/yr maintenance allowance + 100% compulsory non-refundable tuition fees',
    applicationDeadline: '15 December 2026',
    matchScore: 98,
    requiredDocuments: [
      { name: 'Caste Certificate (Digital Genuineness QR)', description: 'Issued by competent Revenue Authority (Tahsildar)', status: 'ready' },
      { name: 'Income Certificate (FY 2025-26)', description: 'Family income must not exceed ₹2.5 Lakh/annum', status: 'ready' },
      { name: 'Aadhaar Seeded Bank Account', description: 'NPCI mapped active bank account for DBT payment', status: 'ready' },
      { name: 'Previous Year Marksheet (Sem 1-4)', description: 'Certified marksheet showing passing status', status: 'ready' },
      { name: 'College Fee Receipt & Bonafide', description: 'Current academic year admission confirmation', status: 'missing' }
    ],
    isDemo: true,
    demoNote: 'Illustrative Demonstration Record'
  },
  {
    id: 'demo-nsp-merit-means',
    title: 'National Means-cum-Merit Scholarship Scheme (NMMSS)',
    provider: 'Department of School Education & Literacy, Ministry of Education',
    level: 'National / Central',
    targetAudience: 'Meritorious students of economically weaker sections enrolled in Classes IX to XII',
    courseLevel: 'Post-Matric / Higher Secondary',
    maxAnnualIncome: 350000,
    minPercentage: 55,
    eligibleCategories: ['General', 'OBC', 'SC', 'ST', 'EWS'],
    amountPerYear: '₹12,000 / year (₹1,000 per month via DBT)',
    applicationDeadline: '31 December 2026',
    matchScore: 92,
    requiredDocuments: [
      { name: 'Class 8th / 10th Qualified Marksheet', description: 'Minimum 55% marks (50% for SC/ST)', status: 'ready' },
      { name: 'Parental Income Certificate', description: 'Family income from all sources ≤ ₹3.50 Lakh', status: 'ready' },
      { name: 'Government / Local Body School Enrollment', description: 'Student must be studying in Govt or aided school', status: 'missing' },
      { name: 'Bank Passbook Copy (Student Name)', description: 'Aadhaar linked savings bank account', status: 'ready' }
    ],
    isDemo: true,
    demoNote: 'Illustrative Demonstration Record'
  },
  {
    id: 'demo-aicte-pragati',
    title: 'AICTE Pragati Scholarship for Girl Students (Degree & Diploma)',
    provider: 'All India Council for Technical Education (AICTE)',
    level: 'National / Central',
    targetAudience: 'Female students admitted to 1st year degree/diploma technical programs in AICTE approved institutions',
    courseLevel: 'Technical / Professional',
    maxAnnualIncome: 800000,
    minPercentage: 60,
    eligibleCategories: ['General', 'OBC', 'SC', 'ST', 'EWS', 'Minority'],
    amountPerYear: '₹50,000 per annum for every year of study',
    applicationDeadline: '20 December 2026',
    matchScore: 88,
    requiredDocuments: [
      { name: 'Central/State Counselling Admission Letter', description: 'Proof of merit-based admission to AICTE course', status: 'ready' },
      { name: 'Annual Family Income Certificate (< 8 Lakhs)', description: 'Issued by designated state tehsildar/officer', status: 'ready' },
      { name: 'Parental Declaration on Single/Two Girl Children', description: 'Notarized affidavit of eligible family count', status: 'missing' },
      { name: 'Aadhaar Card Copy', description: 'Biometric verified student Aadhaar', status: 'ready' }
    ],
    isDemo: true,
    demoNote: 'Illustrative Demonstration Record'
  },
  {
    id: 'demo-karnataka-epass-vidyasiri',
    title: 'Karnataka Vidyasiri (Food & Accommodation) Scheme',
    provider: 'Backward Classes Welfare Department, Govt of Karnataka',
    level: 'State Gov',
    targetAudience: 'Post-matric students belonging to OBC categories residing in non-hostel private accommodations',
    courseLevel: 'Undergraduate',
    maxAnnualIncome: 250000,
    minPercentage: 50,
    eligibleCategories: ['OBC', 'EWS'],
    amountPerYear: '₹1,500 per month (₹15,000 for 10 academic months)',
    applicationDeadline: '10 January 2027',
    matchScore: 84,
    requiredDocuments: [
      { name: 'Karnataka Domicile Certificate', description: 'Proof of residence in Karnataka for minimum 7 years', status: 'ready' },
      { name: 'OBC Category Certificate (RD Number)', description: 'Verified caste certificate with valid RD barcode', status: 'ready' },
      { name: 'Distance Certificate / Non-allotment of Govt Hostel', description: 'Issued by college Principal confirming > 5km distance', status: 'expiring' },
      { name: 'Student Bank Account (Aadhaar Seeded)', description: 'DBT mandatory bank account', status: 'ready' }
    ],
    isDemo: true,
    demoNote: 'Illustrative Demonstration Record'
  }
];

export const MOCK_CITATIONS: Citation[] = [
  {
    id: 'cite-pmkisan-clause-4',
    title: 'PM-KISAN Operational Guidelines — Section 4 (Beneficiary Definition)',
    documentName: 'Ministry Circular No. 1-1/2019-Credit-I',
    issuingAuthority: 'Department of Agriculture & Farmers Welfare, New Delhi',
    circularNumber: 'DO-AGR-2019/SEC4',
    notificationDate: '01 February 2019 (Amended Aug 2023)',
    clauseNumber: 'Clause 4.1 & Clause 5 (Exclusion Criteria)',
    excerpt: '"A landholder farmer family is defined as a family consisting of husband, wife and minor children who own cultivable land as per land records of the concerned State/UT. Institutional landholders and families where any member is a serving/retired government officer or income-tax assessee stand excluded."',
    officialSourceUrl: 'https://pmkisan.gov.in/Documents/OperationalGuidelines.pdf',
    verificationBadge: 'Official Gazette Grounded'
  },
  {
    id: 'cite-raitha-vidya-sec2',
    title: 'Karnataka Raita Vidya Nidhi Scheme Notification',
    documentName: 'Government Order No. AGRI-2021-KRN-44',
    issuingAuthority: 'Department of Agriculture, Vidhana Soudha, Bengaluru',
    circularNumber: 'GO-AGRI-44-EDN-2021',
    notificationDate: '07 August 2021',
    clauseNumber: 'Clause 3(a) & 3(b) (Farmer Family & Course Eligibility)',
    excerpt: '"Financial assistance under the Raita Vidya Nidhi program shall be transferred directly to the Aadhaar-seeded savings account of eligible wards of registered farmers whose land details are verified in the state FRUITS software."',
    officialSourceUrl: 'https://raitamitra.karnataka.gov.in',
    verificationBadge: 'Karnataka State Gazette Verified'
  },
  {
    id: 'cite-postmatric-sec5',
    title: 'Centrally Sponsored Post Matric Scholarship for SC Guidelines',
    documentName: 'MoSJE Notification F.No. 11014/01/2020-SCD-V',
    issuingAuthority: 'Ministry of Social Justice & Empowerment, Shastri Bhawan',
    circularNumber: 'MOSJE-SCD-V-2020-91',
    notificationDate: '23 December 2020',
    clauseNumber: 'Clause 5.2 (Income Ceiling & Direct Benefit Transfer)',
    excerpt: '"Scholarships will be paid to the students whose parents\'/guardians\' income from all sources does not exceed Rs. 2,50,000/- (Rupees two lakh fifty thousand only) per annum. All disbursements shall be executed via the Aadhaar Payment Bridge (APB)."',
    officialSourceUrl: 'https://socialjustice.gov.in/writereaddata/UploadFile/SC_PMS_2020.pdf',
    verificationBadge: 'Government of India Grounded'
  }
];

export const MOCK_DOCUMENT_ANALYSIS: DocumentAnalysisResult = {
  fileName: 'Karnataka_Raita_Vidya_Nidhi_Gazette_Circular_2024.pdf',
  fileSize: '1.42 MB',
  pages: 8,
  extractedDate: '15 October 2024',
  documentType: 'Official State Government Circular (Bilingual: Kannada & English)',
  issuingDepartment: 'Department of Agriculture, Government of Karnataka',
  executiveSummary: 'This official government circular expands the beneficiary coverage of the Raita Vidya Nidhi education assistance scheme to include children of landless agricultural laborers, fishermen, and weaver households across Karnataka, establishing revised DBT slab rates from ₹2,500 to ₹11,000 per academic year.',
  keyEligibilityRules: [
    {
      criterion: 'Parental Registration in FRUITS or Weaver/Fisherman ID Database',
      officialClause: 'Paragraph 4, Subsection 2.1',
      requirementType: 'Mandatory'
    },
    {
      criterion: 'Active Admission in Recognised Higher Education Institution in Karnataka',
      officialClause: 'Paragraph 5, Subsection 1.4',
      requirementType: 'Mandatory'
    },
    {
      criterion: 'Concurrent Benefit with Other Central/State Merit Scholarships Allowed',
      officialClause: 'Paragraph 7, Clause 3 ("No bar on non-overlapping educational grants")',
      requirementType: 'Relaxation Available'
    },
    {
      criterion: 'Income Certificate required only if Parent is Landless Laborer without FID',
      officialClause: 'Paragraph 6, Subsection 3',
      requirementType: 'Conditional'
    }
  ],
  mandatoryDocumentList: [
    {
      document: 'FRUITS Farmer ID (FID) / Weavers ID Certificate',
      issuingOffice: 'Raitha Samparka Kendra / Gram Panchayat Office',
      criticalNotes: 'Must be active in the state Kutumba digital family registry.'
    },
    {
      document: 'State Scholarship Portal (SSP) Student ID',
      issuingOffice: 'Karnataka SSP Online Portal (ssp.postmatric.karnataka.gov.in)',
      criticalNotes: 'Student profile must be e-KYC authenticated with linked Aadhaar.'
    },
    {
      document: 'College Bonafide Certificate with Study Year',
      issuingOffice: 'Registrar / Principal of Enrolled College / University',
      criticalNotes: 'Must clearly state current semester and course duration.'
    },
    {
      document: 'Aadhaar-Seeded Bank Account (NPCI Active Status)',
      issuingOffice: 'Bank Branch with Core Banking / NPCI Clearing',
      criticalNotes: 'Account must have DBT mandate enabled, not simple account linking.'
    }
  ],
  criticalDeadlines: [
    {
      milestone: 'Fresh College SSP Student Registration',
      deadlineDate: '30 November 2026',
      consequence: 'Late filings will not be eligible for the 1st installment disbursement cycle.'
    },
    {
      milestone: 'Institutional Verification & Principal Approval',
      deadlineDate: '15 December 2026',
      consequence: 'Unverified forms get rejected at the Taluk Social Welfare Officer scrutiny stage.'
    },
    {
      milestone: 'DBT Payment Disbursal to Bank Account',
      deadlineDate: 'January - February 2027',
      consequence: 'Disbursement through Aadhaar Payment Bridge (APB).'
    }
  ],
  flaggedAmbiguities: [
    'The circular does not specify if students repeating a year (due to backlogs) are eligible for renewal or if fresh registration is necessary.',
    'Differing guidelines exist for private deemed university students regarding hostel allowances vs tuition waivers.'
  ],
  isDemo: true
};

export const SAMPLE_CHAT_HISTORY: { [key: string]: { userPrompt: string; aiResponse: string; citations: Citation[] } } = {
  kisan: {
    userPrompt: "Am I eligible for PM-KISAN if my family has 3 acres of agricultural land in Karnataka?",
    aiResponse: "Yes, you are likely eligible under the small and marginal landholding criteria of PM-KISAN, provided you meet specific exclusions:\n\n1. **Land Ownership**: You must possess valid Record of Rights (Pahani / RTC) in your name or your family member's name showing cultivable agricultural land.\n2. **Exclusion Conditions**: None of your family members (husband, wife, minor children) must be:\n   - An institutional landholder\n   - A serving or retired government employee / pensioner drawing ≥ ₹10,000/month\n   - An income tax assessee for the latest assessment year.\n3. **Mandatory Action**: Ensure your Aadhaar is biometric e-KYC verified on pmkisan.gov.in and your bank account is mapped to NPCI for Direct Benefit Transfer (DBT).",
    citations: [MOCK_CITATIONS[0]]
  },
  scholarship: {
    userPrompt: "What is the annual income limit for the Central Post-Matric Scholarship for SC students?",
    aiResponse: "According to the official Ministry of Social Justice & Empowerment guidelines:\n\n- **Annual Family Income Ceiling**: The total annual income of parents/guardians from all sources must **not exceed ₹2,50,000 (Rupees Two Lakh Fifty Thousand)** per annum.\n- **Evidence Required**: A computerized Income Certificate issued by the designated state authority (such as the Tahsildar with digital signature or QR code) is strictly mandatory.\n- **Tuition & Maintenance**: The scheme provides full non-refundable compulsory fees reimbursement plus an annual maintenance allowance up to ₹13,500 for hostellers (or ₹7,000 for day scholars) depending on the course group.",
    citations: [MOCK_CITATIONS[2]]
  },
  kannada: {
    userPrompt: "ರೈತ ವಿದ್ಯಾನಿಧಿ ವಿದ್ಯಾರ್ಥಿವೇತನಕ್ಕೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಅಗತ್ಯವಿರುವ ಮುಖ್ಯ ದಾಖಲೆಗಳು ಯಾವುವು?",
    aiResponse: "ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಕೃಷಿ ಇಲಾಖೆಯ ಅಧಿಕೃತ ಸುತ್ತೋಲೆಯ ಪ್ರಕಾರ, ರೈತ ವಿದ್ಯಾನಿಧಿ ಯೋಜನೆಗೆ ಕೆಳಗಿನ ಪ್ರಮುಖ ದಾಖಲೆಗಳು ಅತ್ಯಗತ್ಯ:\n\n1. **ರೈತ ಗುರುತಿನ ಚೀಟಿ (FRUITS FID)**: ಪೋಷಕರ ಹೆಸರಿನಲ್ಲಿರುವ ಕರ್ನಾಟಕ ಸರ್ಕಾರದ FRUITS ತಂತ್ರಾಂಶದಲ್ಲಿ ನೋಂದಾಯಿತ FID ಸಂಖ್ಯೆ.\n2. **ವಿದ್ಯಾರ್ಥಿಯ SSP ಐಡಿ**: ರಾಜ್ಯ ವಿದ್ಯಾರ್ಥಿವೇತನ ತಂತ್ರಾಂಶದಲ್ಲಿ (State Scholarship Portal) ಸಕ್ರಿಯ ವಿದ್ಯಾರ್ಥಿ ನೋಂದಣಿ ಸಂಖ್ಯೆ.\n3. **ಆಧಾರ್ ಲಿಂಕ್ಡ್ ಬ್ಯಾಂಕ್ ಖಾತೆ**: ವಿದ್ಯಾರ್ಥಿಯ ಸ್ವಂತ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಆಧಾರ್ ಸೀಡಿಂಗ್ (NPCI ಮ್ಯಾಪಿಂಗ್) ಪೂರ್ಣಗೊಂಡಿರಬೇಕು.\n4. **ಕಾಲೇಜು ಬೋನಾಫೈಡ್ ಪ್ರಮಾಣಪತ್ರ**: ಪ್ರಸ್ತುತ ಶೈಕ್ಷಣಿಕ ವರ್ಷದಲ್ಲಿ ಮಾನ್ಯತೆ ಪಡೆದ ಕಾಲೇಜಿನಲ್ಲಿ ಓದುತ್ತಿರುವ ಬಗ್ಗೆ ಕಾಲೇಜು ಪ್ರಾಚಾರ್ಯರ ದೃಢೀಕರಣ ಪತ್ರ.\n\nಗಮನಿಸಿ: ಈ ಯೋಜನೆಯ ಹಣವನ್ನು ನೇರವಾಗಿ ವಿದ್ಯಾರ್ಥಿಯ ಆಧಾರ್ ಲಿಂಕ್ ಆದ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ DBT ಮೂಲಕ ವರ್ಗಾಯಿಸಲಾಗುತ್ತದೆ.",
    citations: [MOCK_CITATIONS[1]]
  }
};
