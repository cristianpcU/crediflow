from django.core.management.base import BaseCommand
from django.utils import timezone
from loans.models import Cuota


class Command(BaseCommand):
    help = 'Actualiza el estado de las cuotas pendientes a vencido si la fecha de vencimiento ya pasó'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin hacer cambios reales en la base de datos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Obtener cuotas pendientes que ya vencieron
        cuotas_a_actualizar = Cuota.objects.filter(
            estado='PENDIENTE',
            fecha_vencimiento__lt=timezone.now().date()
        )
        
        count = cuotas_a_actualizar.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Se actualizarían {count} cuota(s) a estado VENCIDO'
                )
            )
            
            for cuota in cuotas_a_actualizar[:10]:  # Mostrar solo las primeras 10
                self.stdout.write(
                    f'  - Cuota #{cuota.numero_cuota} del préstamo #{cuota.prestamo.id} '
                    f'(Cliente: {cuota.prestamo.cliente}) - Vencimiento: {cuota.fecha_vencimiento}'
                )
            
            if count > 10:
                self.stdout.write(f'  ... y {count - 10} más')
        else:
            # Actualizar las cuotas
            updated = cuotas_a_actualizar.update(estado='VENCIDO')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Se actualizaron {updated} cuota(s) a estado VENCIDO'
                )
            )
            
            # Mostrar detalles de las cuotas actualizadas
            if updated > 0:
                self.stdout.write('\nCuotas actualizadas:')
                for cuota in Cuota.objects.filter(
                    estado='VENCIDO',
                    fecha_vencimiento__lt=timezone.now().date()
                )[:10]:
                    self.stdout.write(
                        f'  - Cuota #{cuota.numero_cuota} del préstamo #{cuota.prestamo.id} '
                        f'(Cliente: {cuota.prestamo.cliente}) - Vencimiento: {cuota.fecha_vencimiento}'
                    )
                
                if updated > 10:
                    self.stdout.write(f'  ... y {updated - 10} más')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Comando ejecutado exitosamente')
