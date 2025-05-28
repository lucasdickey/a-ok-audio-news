from django.core.management.base import BaseCommand
from django.utils import timezone
from digests.models import DailyDigest
from datetime import date, datetime, timedelta
import re

class Command(BaseCommand):
    help = 'Comprehensive review of pipeline output quality and format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to review (YYYY-MM-DD format)',
            default=str(timezone.now().date())
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show full script content'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Pipeline Output Review'))
        self.stdout.write('=' * 60)
        
        target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        
        try:
            digest = DailyDigest.objects.get(date=target_date)
            script = digest.summary_text_en
            
            self.stdout.write(f"📅 Reviewing script for: {target_date}")
            self.stdout.write(f"📏 Script length: {len(script)} characters")
            
            # === CRITICAL ISSUES ANALYSIS ===
            self.stdout.write(self.style.WARNING('\n🚨 CRITICAL ISSUES:'))
            
            issues = []
            
            # Check for AI search process leakage
            search_indicators = [
                "Let me search",
                "I'll search for",
                "Based on the search results",
                "Let me verify",
                "I need to search"
            ]
            
            search_leakage = any(indicator in script for indicator in search_indicators)
            if search_leakage:
                issues.append("❌ AI search process visible in final script")
                for indicator in search_indicators:
                    if indicator in script:
                        count = script.count(indicator)
                        self.stdout.write(f"   - '{indicator}': {count} occurrences")
            
            # Check format requirements
            has_proper_opening = "Hello world" in script and "Apes On Knowledge" in script
            has_proper_closing = "A-OK Newsbot" in script and "signing off" in script
            
            if not has_proper_opening:
                issues.append("❌ Missing proper opening format")
            if not has_proper_closing:
                issues.append("❌ Missing proper closing format")
            
            # Story count analysis
            story_patterns = [
                r'STORY \d+:',
                r'Story \d+:',
                r'\d+\.',  # numbered list
            ]
            
            story_count = 0
            for pattern in story_patterns:
                matches = re.findall(pattern, script)
                story_count = max(story_count, len(matches))
            
            if story_count < 10:
                issues.append(f"❌ Only {story_count} stories found (need 10)")
            elif story_count > 10:
                issues.append(f"❌ Too many stories: {story_count} (need exactly 10)")
            
            # Citation analysis
            citation_patterns = [
                r'reports in [\'"].*[\'"]',
                r'according to [A-Z][a-zA-Z\s]+',
                r'[A-Z][a-zA-Z\s]+ reports',
                r'announced in',
                r'published in'
            ]
            
            citation_count = 0
            for pattern in citation_patterns:
                citation_count += len(re.findall(pattern, script, re.IGNORECASE))
            
            if citation_count < 5:
                issues.append(f"❌ Insufficient citations: {citation_count} (need 5+ for credibility)")
            
            # Date freshness check
            yesterday = target_date - timedelta(days=1)
            date_mentions = script.count(str(target_date)) + script.count(str(yesterday))
            
            if date_mentions == 0:
                issues.append("❌ No date mentions (may be using old news)")
            
            # Hallucination indicators (removed o3/o4-mini as these models exist)
            hallucination_flags = [
                # Note: Removed o3/o4-mini as these are real OpenAI models
                # "$65 billion",     # Large investment numbers should be verified but not flagged as hallucination
                # "1 gigawatt",      # Technical claims should be verified but not automatically flagged
            ]
            
            for flag in hallucination_flags:
                if flag in script:
                    issues.append(f"⚠️  Potential hallucination: '{flag}' needs verification")
            
            # === SUMMARY ===
            if issues:
                self.stdout.write(f"\n❌ Found {len(issues)} issues:")
                for issue in issues:
                    self.stdout.write(f"   {issue}")
            else:
                self.stdout.write(self.style.SUCCESS("\n✅ No critical issues found!"))
            
            # === QUALITY METRICS ===
            self.stdout.write(self.style.WARNING('\n📊 QUALITY METRICS:'))
            self.stdout.write(f"✅ Proper opening: {'Yes' if has_proper_opening else 'No'}")
            self.stdout.write(f"✅ Proper closing: {'Yes' if has_proper_closing else 'No'}")
            self.stdout.write(f"📊 Story count: {story_count}/10")
            self.stdout.write(f"📰 Citations found: {citation_count}")
            self.stdout.write(f"📅 Date references: {date_mentions}")
            self.stdout.write(f"🔍 Search leakage: {'Yes' if search_leakage else 'No'}")
            
            # === CONTENT PREVIEW ===
            if options['verbose'] or search_leakage:
                self.stdout.write(self.style.WARNING('\n📄 SCRIPT CONTENT:'))
                self.stdout.write('-' * 60)
                self.stdout.write(script)
                self.stdout.write('-' * 60)
            else:
                self.stdout.write(f"\n📄 Script preview (first 400 chars):")
                self.stdout.write('-' * 40)
                preview = script[:400] + "..." if len(script) > 400 else script
                self.stdout.write(preview)
                self.stdout.write('-' * 40)
            
            # === RECOMMENDATIONS ===
            if issues:
                self.stdout.write(self.style.WARNING('\n💡 RECOMMENDATIONS:'))
                
                if search_leakage:
                    self.stdout.write("   🔧 Fix search leakage: Update agents to return only final content")
                    self.stdout.write("   🔧 Add content filtering to remove AI process text")
                
                if story_count != 10:
                    self.stdout.write("   🔧 Fix story count: Update prioritizer agent constraints")
                
                if citation_count < 5:
                    self.stdout.write("   🔧 Improve citations: Enhance source citation prompts")
                
                if date_mentions == 0:
                    self.stdout.write("   🔧 Enforce date constraints: Add 24-hour verification")
            
            # === SCORE ===
            score = 100
            score -= len([i for i in issues if i.startswith('❌')]) * 20
            score -= len([i for i in issues if i.startswith('⚠️')]) * 10
            score = max(0, score)
            
            if score >= 80:
                style = self.style.SUCCESS
            elif score >= 60:
                style = self.style.WARNING
            else:
                style = self.style.ERROR
            
            self.stdout.write(style(f'\n🎯 QUALITY SCORE: {score}/100'))
            
        except DailyDigest.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ No script found for {target_date}'))
            self.stdout.write('   Available dates:')
            for digest in DailyDigest.objects.order_by('-date')[:5]:
                self.stdout.write(f'   - {digest.date}') 