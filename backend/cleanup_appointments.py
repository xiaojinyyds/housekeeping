from app.core.database import SessionLocal, engine
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('appointments')
    existing_columns = {col['name'] for col in columns}
    
    # Columns defined in app/models/appointment.py
    model_columns = {
        'id', 'order_no', 'user_id', 'worker_id', 'service_id', 'service_name',
        'appointment_date', 'time_slot_id', 'time_slot_name', 'duration_hours',
        'unit_price', 'total_price', 'address', 'contact_name', 'contact_phone',
        'remark', 'status', 'reject_reason', 'cancel_reason', 'cancelled_by',
        'accepted_at', 'started_at', 'completed_at', 'cancelled_at',
        'created_at', 'updated_at'
    }
    
    # Identify columns to drop
    # Only drop columns that are NOT in model_columns
    # BE CAREFUL: some columns might be named differently in DB?
    # Based on previous analysis:
    # DB has: 'start_time', 'end_time', 'rating', 'review', 'reviewed_at', 'payment_status', 'payment_method', 'transaction_id'
    # And potentially 'appointment_time' if it exists (though previous checks were ambiguous, the error says it exists)
    
    columns_to_drop = []
    for col_name in existing_columns:
        if col_name not in model_columns:
            columns_to_drop.append(col_name)
    
    logger.info(f"Columns to drop: {columns_to_drop}")
    
    db = SessionLocal()
    try:
        if columns_to_drop:
            # Drop one by one to avoid syntax errors if multiple
            for col in columns_to_drop:
                # Check for Foreign Keys first? 
                # If a column has FK, we might need to drop FK first.
                # Simplification: just try to drop column.
                logger.info(f"Dropping column: {col}")
                try:
                    # Some columns might have foreign keys constraints, let's try to drop constraint if error?
                    # But for now simple drop.
                    # MySQL syntax: ALTER TABLE tbl DROP COLUMN col
                    db.execute(text(f"ALTER TABLE appointments DROP COLUMN {col}"))
                    db.commit()
                    logger.info(f"Dropped {col}")
                except Exception as e:
                    logger.error(f"Failed to drop {col}: {e}")
                    # If it fails due to FK, we might need to find FK name and drop it.
                    # But legacy columns usually don't have FKs except maybe user_id/worker_id which we keep.
                    # 'transaction_id' might refer to payments table?
                    db.rollback()
        else:
            logger.info("No columns to drop.")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_schema()
