// Type definitions for review system

export enum ReviewItemStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export enum ReviewItemType {
  ENTITY = 'entity',
  RELATIONSHIP = 'relationship',
}

export interface EntityData {
  name: string;
  type: string;
  description?: string;
  confidence: number;
  source_reference?: string;
  metadata?: Record<string, any>;
}

export interface RelationshipData {
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  confidence: number;
  source_reference?: string;
  metadata?: Record<string, any>;
}

export interface ReviewItem {
  id: string;
  type: ReviewItemType;
  status: ReviewItemStatus;
  user_id: string;
  source_document_id: string;
  extracted_at: string;
  data: EntityData | RelationshipData;
  reviewed_at?: string;
  reviewed_by?: string;
  rejection_reason?: string;
  metadata?: Record<string, any>;
}

export interface UserStats {
  user_id: string;
  total_items: number;
  pending_items: number;
  approved_items: number;
  rejected_items: number;
  created_at: string;
  updated_at: string;
}

export interface BatchOperation {
  operation_id: string;
  item_ids: string[];
  operation_type: 'approve' | 'reject';
  reason?: string;
  created_at: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
}

export interface BatchResult {
  operation_id: string;
  total_items: number;
  successful_items: number;
  failed_items: number;
  results: Array<{
    item_id: string;
    success: boolean;
    error?: string;
  }>;
  created_at: string;
  completed_at?: string;
}

export interface ReviewQueueResponse {
  items: ReviewItem[];
  count: number;
  filters: {
    limit: number;
    min_confidence: number;
    type?: string;
    order_by: string;
    descending: boolean;
  };
}

// Component props interfaces
export interface EntityCardProps {
  entity: ReviewItem;
  onApprove: (itemId: string) => void;
  onReject: (itemId: string, reason?: string) => void;
  isSelected?: boolean;
  onSelect?: (itemId: string) => void;
}

export interface RelationshipCardProps {
  relationship: ReviewItem;
  onApprove: (itemId: string) => void;
  onReject: (itemId: string, reason?: string) => void;
  isSelected?: boolean;
  onSelect?: (itemId: string) => void;
}

export interface ConfidenceBadgeProps {
  confidence: number;
  size?: 'sm' | 'md' | 'lg';
}