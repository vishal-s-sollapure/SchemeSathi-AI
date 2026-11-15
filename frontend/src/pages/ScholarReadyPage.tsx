import React, { useState } from 'react';
import { 
  GraduationCap, 
  FileCheck2, 
  Search, 
  CheckCircle2, 
  XCircle, 
  FileWarning, 
  UserCheck, 
  Award,
  Info
} from 'lucide-react';
import { ScholarshipCard } from '../components/common/ScholarshipCard';
import { MOCK_SCHOLARSHIPS } from '../data/mockData';
import { StudentProfile } from '../types';

export const ScholarReadyPage: React.FC = () => {
  // 1. Student Profile State
  const [profile, setProfile] = useState<StudentProfile>({
    fullName: 'Ananya Sharma',
    domicileState: 'Karnataka',
    category: 'OBC',
    annualFamilyIncome: 180000, // 1.8 Lakhs
    currentCourse: 'B.E. Computer Science & Engineering',
    yearOfStudy: '3rd Year',
    marksPercentage: 84.5,
    gender: 'Female',
    disabilityStatus: false,
    hostellerStatus: 'Day Scholar'
  });

  // 2. Interactive Document Readiness Checklist State
  const [documentChecklist, setDocumentChecklist] = useState([
    {
      id: 'doc-income',
      name: 'Family Income Certificate (Current FY 2025-26)',
      authority: 'Revenue Department / Tahsildar (e-Pramaan Patra)',
      status: 'ready' as 'ready' | 'missing' | 'expiring',
      validity: 'Valid through 31 March 2027',
      criticalFor: 'All Means-based Schemes (< 2.5L / < 3.5L)'
    },
    {
      id: 'doc-caste',
      name: 'OBC / Caste Certificate with Digital QR & RD Number',
      authority: 'Nadakacheri / Taluk Revenue Office',
      status: 'ready' as 'ready' | 'missing' | 'expiring',
      validity: 'Permanent / Verified against state registry',
      criticalFor: 'Central Post-Matric & Vidyasiri Schemes'
    },
    {
      id: 'doc-bonafide',
      name: 'College Current Academic Year Bonafide Certificate',
      authority: 'Principal / Registrar of Enrolled College',
      status: 'missing' as 'ready' | 'missing' | 'expiring',
      validity: 'Needs renewal for Year 3',
      criticalFor: 'Mandatory on NSP & Karnataka SSP'
    },
    {
      id: 'doc-bank',
      name: 'Aadhaar-Seeded Bank Passbook (NPCI DBT Active)',
      authority: 'Designated Core Banking Branch',
      status: 'ready' as 'ready' | 'missing' | 'expiring',
      validity: 'NPCI Active Status Confirmed',
      criticalFor: 'Direct Benefit Transfer (DBT) Payouts'
    },
    {
      id: 'doc-marksheet',
      name: 'Certified Previous Semester Grade Cards (Sem 1-4)',
      authority: 'University Examination Controller',
      status: 'ready' as 'ready' | 'missing' | 'expiring',
      validity: '84.5% Aggregate Certified',
      criticalFor: 'Merit-cum-Means & Pragati Evaluation'
    },
    {
      id: 'doc-hostel',
      name: 'Hostel Distance Certificate / Private Accommodation Rent Slip',
      authority: 'Warden / Registered Landlord & Principal Endorsement',
      status: 'expiring' as 'ready' | 'missing' | 'expiring',
      validity: 'Expiring in 18 days',
      criticalFor: 'Vidyasiri Food & Accommodation Allowance'
    }
  ]);

  // Filters State
  const [selectedLevel, setSelectedLevel] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [girlsOnlyFilter, setGirlsOnlyFilter] = useState(false);

  // Toggle document status interactively
  const handleToggleDocStatus = (id: string) => {
    setDocumentChecklist(prev =>
      prev.map(item => {
        if (item.id === id) {
          const nextStatus = item.status === 'ready' ? 'missing' : item.status === 'missing' ? 'expiring' : 'ready';
          return { ...item, status: nextStatus };
        }
        return item;
      })
    );
  };

  // Calculate live readiness score
  const readyCount = documentChecklist.filter(d => d.status === 'ready').length;
  const totalCount = documentChecklist.length;
  const readinessScore = Math.round((readyCount / totalCount) * 100);

  // Filter scholarships
  const filteredScholarships = MOCK_SCHOLARSHIPS.filter(sch => {
    if (selectedLevel !== 'All' && !sch.level.includes(selectedLevel)) return false;
    if (girlsOnlyFilter && !sch.targetAudience.toLowerCase().includes('girl') && !sch.title.toLowerCase().includes('pragati')) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return sch.title.toLowerCase().includes(q) || sch.provider.toLowerCase().includes(q) || sch.courseLevel.toLowerCase().includes(q);
    }
    return true;
  });

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-ashoka-900 via-ashoka-800 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-elevated relative overflow-hidden">
        <div className="relative max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold bg-ashoka-700/80 text-ashoka-100 px-3 py-1 rounded-full border border-ashoka-500">
            <GraduationCap className="w-4 h-4 text-emerald-300" />
            <span>ScholarReady™ Student Intelligence Center</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Check Your Scholarship Eligibility &amp; Application Readiness
          </h1>
          <p className="text-xs sm:text-sm text-ashoka-100/90 leading-relaxed">
            Configure your student credentials below. Our deterministic engine maps your profile against Central Sector, AICTE, and Karnataka state schemes, identifying missing documents before you submit on official portals.
          </p>
        </div>
      </div>

      {/* 2-Column Main Workspace: Profile Entry (Left) + Readiness Overview (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT COLUMN: Student Profile Entry Form (5 Cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <UserCheck className="w-5 h-5 text-ashoka-700" />
              <h2 className="text-base font-bold text-charcoal-900">
                Student Profile Parameters
              </h2>
            </div>
            <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              Interactive Form
            </span>
          </div>

          <p className="text-xs text-slate-500">
            Adjust your academic and economic details to see real-time eligibility updates.
          </p>

          <form onSubmit={(e) => e.preventDefault()} className="space-y-4 text-xs font-medium text-slate-700">
            {/* Full Name */}
            <div>
              <label className="block text-slate-600 mb-1 font-semibold">Full Name</label>
              <input
                type="text"
                value={profile.fullName}
                onChange={(e) => setProfile({ ...profile, fullName: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-ashoka-600 font-sans text-xs"
              />
            </div>

            {/* Domicile State & Caste Category */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-600 mb-1 font-semibold">Domicile State</label>
                <select
                  value={profile.domicileState}
                  onChange={(e) => setProfile({ ...profile, domicileState: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-ashoka-600 text-xs bg-white"
                >
                  <option value="Karnataka">Karnataka</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Uttar Pradesh">Uttar Pradesh</option>
                  <option value="Tamil Nadu">Tamil Nadu</option>
                  <option value="Delhi">Delhi</option>
                  <option value="Other States">Other States</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 mb-1 font-semibold">Social Category</label>
                <select
                  value={profile.category}
                  onChange={(e) => setProfile({ ...profile, category: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-ashoka-600 text-xs bg-white"
                >
                  <option value="General">General / Unreserved</option>
                  <option value="OBC">OBC (Category 2A, 3A, 3B)</option>
                  <option value="SC">Scheduled Caste (SC)</option>
                  <option value="ST">Scheduled Tribe (ST)</option>
                  <option value="EWS">Economically Weaker Section (EWS)</option>
                  <option value="Minority">Religious Minority</option>
                </select>
              </div>
            </div>

            {/* Annual Family Income Slider */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-slate-600 font-semibold">Annual Family Income</label>
                <span className="font-extrabold text-ashoka-800 bg-ashoka-50 px-2 py-0.5 rounded border border-ashoka-200">
                  ₹{(profile.annualFamilyIncome / 100000).toFixed(2)} Lakhs
                </span>
              </div>
              <input
                type="range"
                min="50000"
                max="1000000"
                step="25000"
                value={profile.annualFamilyIncome}
                onChange={(e) => setProfile({ ...profile, annualFamilyIncome: Number(e.target.value) })}
                className="w-full accent-ashoka-700 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>₹50K (BPL)</span>
                <span>₹2.5L (Post-Matric Cap)</span>
                <span>₹8L (AICTE / Creamy Layer)</span>
              </div>
            </div>

            {/* Course & Academic Marks */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-600 mb-1 font-semibold">Course Level</label>
                <select
                  value={profile.currentCourse}
                  onChange={(e) => setProfile({ ...profile, currentCourse: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-ashoka-600 text-xs bg-white"
                >
                  <option value="B.E. Computer Science & Engineering">B.Tech / B.E. (Technical)</option>
                  <option value="B.Sc / B.Com / B.A.">Undergraduate Degree (Non-Tech)</option>
                  <option value="Class 11 / 12 (Pre-University)">Higher Secondary / PUC</option>
                  <option value="Diploma in Engineering">Polytechnic Diploma</option>
                  <option value="M.Tech / M.Sc / MBA">Postgraduate</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 mb-1 font-semibold">Marks / CGPA (%)</label>
                <input
                  type="number"
                  min="35"
                  max="100"
                  step="0.5"
                  value={profile.marksPercentage}
                  onChange={(e) => setProfile({ ...profile, marksPercentage: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-ashoka-600 text-xs"
                />
              </div>
            </div>

            {/* Gender & Hostel Status */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-600 mb-1 font-semibold">Gender</label>
                <select
                  value={profile.gender}
                  onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-ashoka-600 text-xs bg-white"
                >
                  <option value="Female">Female</option>
                  <option value="Male">Male</option>
                  <option value="Other">Other / Non-binary</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 mb-1 font-semibold">Accommodation</label>
                <select
                  value={profile.hostellerStatus}
                  onChange={(e) => setProfile({ ...profile, hostellerStatus: e.target.value as any })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-ashoka-600 text-xs bg-white"
                >
                  <option value="Day Scholar">Day Scholar</option>
                  <option value="Hosteller">Hosteller (College/Govt)</option>
                </select>
              </div>
            </div>

            <div className="pt-2 text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              Evaluations are deterministic. Rules verify: <code className="text-ashoka-800 font-mono">Income ≤ Scheme Ceiling &amp;&amp; Marks ≥ Threshold</code>.
            </div>
          </form>
        </div>

        {/* RIGHT COLUMN: Application Readiness Overview & Checklist (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Readiness Meter Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Live Application Readiness Overview
                </div>
                <h3 className="text-xl font-bold text-charcoal-900 mt-0.5">
                  Your Preparation Score: {readinessScore}%
                </h3>
                <p className="text-xs text-slate-600 mt-1">
                  {readinessScore === 100 
                    ? '🎉 Excellent! All required documents verified for instant submission.'
                    : `⚠️ You have ${totalCount - readyCount} item(s) pending or expiring soon.`
                  }
                </p>
              </div>

              {/* Progress Circle or Meter */}
              <div className="flex items-center gap-3">
                <div className="text-center px-4 py-2 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-2xl font-black text-govgreen-800">
                    {readyCount} / {totalCount}
                  </span>
                  <div className="text-[10px] text-slate-500 uppercase font-bold">
                    Documents Ready
                  </div>
                </div>
              </div>
            </div>

            {/* Visual Progress Bar */}
            <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden p-0.5">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  readinessScore >= 80 ? 'bg-gradient-to-r from-govgreen-600 to-emerald-500' :
                  readinessScore >= 50 ? 'bg-gradient-to-r from-amber-500 to-amber-400' :
                  'bg-gradient-to-r from-rose-500 to-orange-500'
                }`}
                style={{ width: `${readinessScore}%` }}
              />
            </div>
          </div>

          {/* Interactive Document Checklist */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-govgreen-700" />
                <h3 className="text-sm font-bold text-charcoal-900">
                  Mandatory Document Verification Checklist
                </h3>
              </div>
              <span className="text-[10px] text-slate-500">
                Click any tag to toggle status
              </span>
            </div>

            <div className="space-y-2.5">
              {documentChecklist.map((doc) => (
                <div
                  key={doc.id}
                  className={`p-3.5 rounded-xl border transition flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                    doc.status === 'ready' ? 'bg-emerald-50/40 border-emerald-200' :
                    doc.status === 'expiring' ? 'bg-amber-50/40 border-amber-200' :
                    'bg-rose-50/40 border-rose-200'
                  }`}
                >
                  <div className="flex items-start gap-2.5">
                    {doc.status === 'ready' ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                    ) : doc.status === 'expiring' ? (
                      <FileWarning className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-500 mt-0.5 flex-shrink-0" />
                    )}

                    <div className="space-y-0.5">
                      <div className="text-xs font-bold text-charcoal-900">
                        {doc.name}
                      </div>
                      <div className="text-[11px] text-slate-500">
                        Issuing Authority: <span className="font-medium text-slate-700">{doc.authority}</span>
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Critical For: {doc.criticalFor}
                      </div>
                    </div>
                  </div>

                  {/* Toggle button */}
                  <button
                    onClick={() => handleToggleDocStatus(doc.id)}
                    className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border transition self-start sm:self-center ${
                      doc.status === 'ready' 
                        ? 'bg-emerald-100 text-emerald-900 border-emerald-300 hover:bg-emerald-200' 
                        : doc.status === 'expiring'
                        ? 'bg-amber-100 text-amber-900 border-amber-300 hover:bg-amber-200'
                        : 'bg-rose-100 text-rose-900 border-rose-300 hover:bg-rose-200'
                    }`}
                    title="Click to cycle status"
                  >
                    {doc.status === 'ready' ? '✓ Ready' : doc.status === 'expiring' ? '⏳ Expiring' : '✗ Missing'}
                  </button>
                </div>
              ))}
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5 text-ashoka-700" />
                Missing documents trigger immediate conditional alerts in NSP/SSP.
              </span>
              <button 
                onClick={() => setDocumentChecklist(prev => prev.map(d => ({ ...d, status: 'ready' })))}
                className="text-[11px] font-semibold text-ashoka-700 hover:underline flex-shrink-0"
              >
                Mark All Ready
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 3. SCHOLARSHIP DISCOVERY AREA & FILTERS */}
      <section className="space-y-6 pt-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-charcoal-900 flex items-center gap-2">
              <Award className="w-5 h-5 text-ashoka-700" />
              <span>Matched Scholarships for Ananya&apos;s Profile</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Showing {filteredScholarships.length} scholarships matching Karnataka Domicile &bull; Income ≤ ₹1.80L
            </p>
          </div>

          {/* Quick Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search scholarship name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-lg border border-slate-300 text-xs focus:outline-none focus:border-ashoka-600 w-48 sm:w-64"
              />
            </div>

            <div className="flex items-center bg-white border border-slate-200 rounded-lg p-0.5 text-xs font-semibold">
              {['All', 'National', 'State'].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setSelectedLevel(lvl)}
                  className={`px-3 py-1 rounded-md transition ${
                    selectedLevel === lvl 
                      ? 'bg-ashoka-700 text-white shadow-sm' 
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>

            <button
              onClick={() => setGirlsOnlyFilter(!girlsOnlyFilter)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition ${
                girlsOnlyFilter 
                  ? 'bg-purple-100 text-purple-900 border-purple-300' 
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              Girls&apos; Schemes Only
            </button>
          </div>
        </div>

        {/* Scholarships Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredScholarships.map((sch) => (
            <ScholarshipCard key={sch.id} scholarship={sch} />
          ))}
        </div>
      </section>
    </div>
  );
};
