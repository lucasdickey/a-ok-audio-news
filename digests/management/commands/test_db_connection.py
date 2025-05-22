from django.core.management.base import BaseCommand
from django.db import connection
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Tests the connection to the Supabase database'

    def handle(self, *args, **options):
        self.stdout.write('Testing database connection...')
        
        try:
            # Check if DATABASE_URL is set
            if not os.getenv('DATABASE_URL'):
                self.stdout.write(self.style.ERROR('DATABASE_URL environment variable is not set'))
                return

            # Try to execute a simple query
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                
            self.stdout.write(self.style.SUCCESS(f'Successfully connected to database!'))
            self.stdout.write(f'Database version: {version[0]}')
            
            # Test DailyDigest table
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'digests_dailydigest'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
            if table_exists:
                self.stdout.write(self.style.SUCCESS('DailyDigest table exists'))
            else:
                self.stdout.write(self.style.WARNING('DailyDigest table does not exist yet'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to connect to database: {str(e)}')) 