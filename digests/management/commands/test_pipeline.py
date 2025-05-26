from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import sys

class Command(BaseCommand):
    help = 'Test the agents pipeline with real API calls'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date for the test (YYYY-MM-DD format)',
            default=str(timezone.now().date())
        )
        parser.add_argument(
            '--no-editor',
            action='store_true',
            help='Skip the editorial review step'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Testing Agents Pipeline via Django'))
        self.stdout.write('=' * 50)
        
        # Import the pipeline
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        from agents_pipeline import generate_episode
        
        # Check API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR('❌ ANTHROPIC_API_KEY not found'))
            return
        
        self.stdout.write(f"✅ API key found: {api_key[:10]}...")
        
        test_date = options['date']
        use_editor = not options['no_editor']
        
        self.stdout.write(f"\n🔬 Testing pipeline:")
        self.stdout.write(f"   📅 Date: {test_date}")
        self.stdout.write(f"   🧠 Editor: {'Enabled' if use_editor else 'Disabled'}")
        
        try:
            self.stdout.write("\n⏳ Running agents pipeline...")
            
            episode_result = generate_episode(
                date_str=test_date,
                with_editor=use_editor,
                human_review=False
            )
            
            self.stdout.write(self.style.SUCCESS('\n✅ Pipeline completed successfully!'))
            
            # Show results
            if episode_result.get('research'):
                self.stdout.write(f"🔍 Research: {len(episode_result['research'])} chars")
                
            if episode_result.get('summary'):
                self.stdout.write(f"📝 Summary: {len(episode_result['summary'])} chars")
                
            if episode_result.get('script'):
                self.stdout.write(f"🎙️ Script: {len(episode_result['script'])} chars")
                self.stdout.write("\n📄 Script Preview:")
                self.stdout.write("-" * 40)
                preview = episode_result['script'][:500] + "..." if len(episode_result['script']) > 500 else episode_result['script']
                self.stdout.write(preview)
                self.stdout.write("-" * 40)
            
            self.stdout.write(self.style.SUCCESS('\n🎉 Test completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Pipeline test failed: {e}'))
            self.stdout.write(self.style.ERROR(f'   Error type: {type(e).__name__}')) 